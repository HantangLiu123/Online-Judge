from typing import Any
import logging
import asyncio
import signal
import aiofiles
import os
import time
import shutil
import traceback
import aiodocker
import psutil
from aiohttp import client_exceptions
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis as aioredis
from tortoise import Tortoise
from shared.models import TestResult, Problem, SubmissionStatus
from shared.schemas import SubmissionTestDetail
from shared.settings import TORTOISE_ORM
from shared.db import language_db, submission_db, resolve_db, user_db
from shared.utils import problem_parse

logging.basicConfig(level=logging.DEBUG)
judge_logger = logging.getLogger('judge')
JUDGE_DIR = '/judge'

async def startup(ctx: dict[Any, Any]):

    """init aiodocker client, fastapi cache, and tortoise"""

    ctx['docker_client'] = aiodocker.Docker()
    await Tortoise.init(TORTOISE_ORM)
    FastAPICache.init(RedisBackend(ctx['redis']), prefix='fastapi_cache')

async def shutdown(ctx: dict[Any, Any]):

    """close the aiodocker client and tortoise"""

    await ctx['docker_client'].close()
    await Tortoise.close_connections()

async def compile_code(
    docker: aiodocker.Docker,
    image_name: str,
    compile_cmd: str,
    submission_id: str,
) -> bool:
    
    """compile the user's code"""

    COMPILE_CONFIG = {
        "Image": image_name,
        "Cmd": compile_cmd.split(),
        "OpenStdin": False,
        "AttachStdin": False,
        "AttachStdout": False,
        "AttachStderr": False,
        "HostConfig": {
            "Binds": [f"/tmp/judge/submission{submission_id}:/workspace"],
            "Memory": 128 * 1024 ** 2,
            "MemorySwap": 256 * 1024 ** 2,
            "NanoCpus": 2_000_000_000,
            "LogConfig": {
                "Type": "none",
            },
        }
    }

    try:
        compile_container = await docker.containers.create(config=COMPILE_CONFIG)
    except aiodocker.DockerError:
        # container creation failed
        judge_logger.error(f'failed to create the container of {image_name}')
        return False
    
    # compile the code
    await compile_container.start()
    result = await asyncio.wait_for(compile_container.wait(), timeout=5)
    await compile_container.delete(force=True)
    return result['StatusCode'] == 0

async def analyze_run_result(
    output: str,
    tle: bool,
    result: dict[str, Any] | None,
    submission_id: str,
):
    
    """analyze the run result"""

    SIG_SUCCESS = 0 

    if tle:
        return TestResult.TLE
    
    # if tle is false, the result should not be none
    assert result is not None
    return_code = result['StatusCode']
    judge_logger.debug(f'return code of submission{submission_id} is {return_code}')
    if return_code > 128:
        return_code -= 128
    if return_code == SIG_SUCCESS:
        # AC or WA
        result_path = os.path.join(JUDGE_DIR, f'submission{submission_id}', 'out.txt')
        async with aiofiles.open(result_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        code_result = content.strip()
        if output == code_result:
            return TestResult.AC
        else:
            return TestResult.WA
        
    elif return_code == signal.SIGHUP or return_code == signal.SIGSEGV \
    or return_code == signal.SIGFPE:
        return TestResult.RE
    
    elif return_code == signal.SIGKILL:
        return TestResult.MLE
    
    else:
        return TestResult.UNK

async def run_code(
    docker: aiodocker.Docker,
    image_name: str,
    run_cmd: str,
    submission_id: str,
    memory_limit: int,
    time_limit: float,
    input: str,
    output: str,
) -> tuple[str, float, int]:
    
    """run the code with the corresponding parameters"""

    RUN_CONFIG = {
        "Image": image_name,
        "Cmd": ["sh", "-c", f"{run_cmd} > /workspace/out.txt 2> /workspace/err.txt"],
        "OpenStdin": True,
        "AttachStdin": True,
        "AttachStdout": False,
        "AttachStderr": False,
        "HostConfig": {
            "Binds": [f"/tmp/judge/submission{submission_id}:/workspace"],
            "Memory": memory_limit * 1024 ** 2,
            "MemorySwap": memory_limit * 2 * 1024 ** 2,
            "NanoCpus": 1_000_000_000,
            "LogConfig": {
                "Type": "none",
            },
        }
    }

    tle = False
    time_used = 0
    max_memory = 0
    result = None

    # create the container
    run_container = await docker.containers.create(RUN_CONFIG)
    web_socket = await run_container.websocket(stdin=True, stream=True)
    await run_container.start()
    
    # get the pid
    info = await run_container.show()
    pid = info['State']['Pid']

    async def send():

        """send the input into the container"""

        try:
            input_with_enter = f'{input}\n'
            await web_socket.send_bytes(input_with_enter.encode())
        except client_exceptions.ClientConnectionError:
            return

    async def monitor_memory():
        
        """monitor the memory with the pid"""

        nonlocal max_memory
        process = psutil.Process(pid)
        try:
            while process.is_running():
                children = process.children()
                if children:
                    target = children[0]
                    current_memory = target.memory_info().rss / 1024 ** 2
                else:
                    current_memory = process.memory_info().rss / 1024 ** 2
                max_memory = max(max_memory, current_memory)
                await asyncio.sleep(0.05)
        except psutil.NoSuchProcess:
            return
        
    monitor_task = asyncio.create_task(monitor_memory())
    input_task = asyncio.create_task(send())
    start_time = time.time()

    try:
        result = await asyncio.wait_for(run_container.wait(), timeout=time_limit)
        time_used = time.time() - start_time
    except asyncio.TimeoutError:
        tle = True
        time_used = time_limit
        
    finally:
        await input_task
        monitor_task.cancel()
        
        status = await analyze_run_result(output, tle, result, submission_id)
        await run_container.delete(force=True)

    return status, time_used, max_memory

async def judge_code(
    submission_id: str,
    language: str,
    problem: Problem,
    code: str,
    docker: aiodocker.Docker,
    redis: aioredis,
) -> list[tuple[TestResult, float, int]]:
    
    """judge the code of the submission"""

    lan_config = await language_db.get_language(language, redis)
    if lan_config is None:
        # the language does not exist for some reason
        judge_logger.error(f'the language {language} does not exist')
        raise EnvironmentError
    
    # create the src file
    ext = lan_config.file_ext
    file_name = f'code.{ext}'
    submission_path = os.path.join(JUDGE_DIR, f'submission{submission_id}')
    if not os.path.exists(submission_path):
        os.mkdir(submission_path)
    async with aiofiles.open(os.path.join(submission_path, file_name), 'w', encoding='utf-8') as f:
        await f.write(code)

    prob = problem_parse.problem_to_problem_schema(problem)
    src = f'/workspace/code.{ext}'
    exe = '/workspace/code'
    if lan_config.compile_cmd is not None:
        compile_cmd = lan_config.compile_cmd.format(src=src, exe=exe)
        cmp_success = await compile_code(
            docker=docker,
            image_name=lan_config.image_name,
            compile_cmd=compile_cmd,
            submission_id=submission_id,
        )
        if not cmp_success:
            shutil.rmtree(submission_path)
            return [(TestResult.CE, 0.0, 0)] * len(prob.testcases)
        
    time_limit = prob.time_limit
    if time_limit is None:
        time_limit = lan_config.time_limit
    memory_limit = prob.memory_limit
    if memory_limit is None:
        memory_limit = lan_config.memory_limit

    # iterate through all tests
    status_list = []
    run_cmd = lan_config.run_cmd.format(src=src, exe=exe)
    for case in prob.testcases:
        status = await run_code(
            docker=docker,
            image_name=lan_config.image_name,
            run_cmd=run_cmd,
            submission_id=submission_id,
            memory_limit=memory_limit,
            time_limit=time_limit,
            input=case.input,
            output=case.output,
        )
        status_list.append(status)

    judge_logger.info(f'submission {submission_id} judged successfuly')
    # remove the files
    shutil.rmtree(submission_path)
    return status_list

def get_score_counts_logs(results: list[tuple[TestResult, float, int]]) -> tuple[int, int, list[SubmissionTestDetail]]:

    """get the score, counts, and logs from the result list"""

    counts = 10 * len(results)
    score = 0
    submission_logs = []
    for i in range(len(results)):
        submission_logs.append(
            SubmissionTestDetail(
                test_id=i + 1,
                result=results[i][0],
                time=results[i][1],
                memory=results[i][2],
            )
        )
        if results[i][0] == TestResult.AC:
            score += 10
    return score, counts, submission_logs

async def update_resolve_relation(
    problem_id: str,
    user_id: int,
    language: str,
    score: int,
    counts: int,
):
    
    """update the resolve status after judging a submission"""

    past_relation = await resolve_db.get_relation_in_db(problem_id, user_id, language)
    if past_relation is None:
        # no records
        new_status = score == counts
        await resolve_db.insert_relation_in_db(problem_id, user_id, language, new_status)
        if new_status:
            user = await user_db.get_user_by_id(user_id)
            if user is None:
                judge_logger.error(f'The user {user_id} does not exist')
            else:
                await user_db.add_resolve_count(user)
    elif past_relation:
        # already resolved
        return
    else:
        # need to update
        new_status = score == counts
        if not new_status:
            return
        else:
            await resolve_db.update_relation_in_db(past_relation, new_status)
            user = await user_db.get_user_by_id(user_id)
            if user is None:
                judge_logger.error(f'The user {user_id} does not exist')
            else:
                await user_db.add_resolve_count(user)

async def judge_task(
    ctx: dict[Any, Any],
    submission_id: str,
):
    
    """judge/rejudge the code"""

    # get the submission
    submission = await submission_db.get_submission_in_db(submission_id)
    if submission is None:
        # the submission does not exist
        judge_logger.error(f'the submission {submission_id} does not exist')
        return
    
    submission_path = os.path.join(JUDGE_DIR, f'submission{submission_id}')

    # judge the code
    try:
        problem = await submission.problem.first()
        results = await judge_code(
            submission_id=submission_id,
            language=submission.language,
            problem=problem,
            code=submission.code,
            docker=ctx['docker_client'],
            redis=ctx['redis'],
        )
        score, counts, submission_logs = get_score_counts_logs(results)
        await submission_db.update_submission_in_db(
            submission=submission,
            status=SubmissionStatus.SUCCESS,
            score=score,
            counts=counts,
            tests=submission_logs,
        )
        await update_resolve_relation(
            problem_id=submission.problem_id, #type: ignore
            user_id=submission.user_id, #type: ignore
            language=submission.language,
            score=score,
            counts=counts
        )
    except EnvironmentError:
        await submission_db.update_submission_in_db(
            submission=submission,
            status=SubmissionStatus.ERROR,
        )
        if os.path.exists(submission_path):
            shutil.rmtree(submission_path)
        judge_logger.error(f'judge of submission {submission_id} failed due to database error')
        tb_str = traceback.format_exc()
        judge_logger.debug(f'Traceback: {tb_str}')
    except Exception as e:
        judge_logger.error(f'judge of submission {submission_id} failed due to unknown error')
        await submission_db.update_submission_in_db(
            submission=submission,
            status=SubmissionStatus.ERROR,
        )
        if os.path.exists(submission_path):
            shutil.rmtree(submission_path)
        tb_str = traceback.format_exc()
        judge_logger.debug(f'Catching the exception: {str(e)} when judging submission{submission_id}. Traceback: {tb_str}')
