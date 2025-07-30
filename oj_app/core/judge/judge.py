import json
import asyncio
import resource
import psutil
import os
import time
import signal
import aiofiles
from typing import Any
from oj_app.models.schemas import SubmissionTestDetail
from oj_app.core.config import logs

TMP_JUDGE_DIR = os.path.join(os.curdir, 'tmp')

def compile_process_limits():

    """a function for limiting the resouce of the compile process
    
    These limits are more than enough for a normal compile process, but they still
    ensure to stop the process when the limits are surpassed
    """

    def limit_compile_resouces():
        resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
        resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 ** 2, 256 * 1024 ** 2))
        resource.setrlimit(resource.RLIMIT_FSIZE, (64 * 1024 ** 2, 64 * 1024 ** 2))

    return limit_compile_resouces

def judge_process_limits(time_limit: float, memory_limit: int):

    """a function for limiting the resouce of the judge subprocess
    
    The limit of the resouce is higher than the actual limit since this is the
    second insurance for the process, which means that it will be triggered only
    when the code from the user surpass the time/memory limit seriously
    """

    def limit_judge_resources():
        resource.setrlimit(resource.RLIMIT_CPU, (int(time_limit * 2), int(time_limit * 2)))
        
        memory_bytes = memory_limit * 1024 ** 2
        resource.setrlimit(resource.RLIMIT_AS, (2 * memory_bytes, 2 * memory_bytes))
        resource.setrlimit(resource.RLIMIT_FSIZE, (1024 ** 2, 1024 ** 2))

    return limit_judge_resources

async def compile(
    submission_id: str,
    lan_config: dict,
) -> int:

    """compile the source code to executable and return the returncode for the process"""

    compile_cmd = lan_config.get('compile_cmd')
    if not compile_cmd:
        # this language does not need to be compiled
        return 0
    
    # compile the source file
    ext = lan_config['file_ext']
    src = f'./code{submission_id}.{ext}'
    exe = f'./code{submission_id}'
    cmd_str = compile_cmd.format(src=src, exe=exe)
    cmd = cmd_str.split()
    compile_process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd = TMP_JUDGE_DIR,
        preexec_fn=compile_process_limits(),
    )
    returncode = await compile_process.wait()
    return returncode

def analyze_run_results(
    output: str,
    returncode: int,
    stdout: bytes | None = None,
    stderr: bytes | None = None,
) -> str:
    
    """Analyze the result of a run.
    
    This function analyzes the result of a run according to its returncode, stdout, 
    and stderr. 

    Args: 
        output (str): the standard output of the testing sample of the problem
        returncode (int): the returncode of the code process
        stdout (bytes | None): the output of the code process
        stderr (bytes | None): the error of the code process

    Returns:
        result_status (str): AC, WA, RE, TLE, MLE, UNK.
    """

    SIG_SUCCESS = 0
    sig_num = -returncode
    if returncode == SIG_SUCCESS:
        # no runtime error, no exceeding limits, just needs to compare the output
        if stdout and stdout.decode().strip() == output:
            status = 'AC'
        else:
            status =  'WA'
    elif returncode == signal.SIGHUP or sig_num == signal.SIGSEGV:
        # determine RE or MLE by stderr
        if stderr and stderr.decode().find('MemoryError') != -1: # python's memory allocation failure
            status = 'MLE'
        else:
            status = 'RE'
    elif sig_num == signal.SIGKILL:
        status = 'MLE'
    elif sig_num == signal.SIGTERM or sig_num == signal.SIGXCPU:
        status = 'TLE'
    elif sig_num == signal.SIGABRT:
        # cpp's memory allocation failure
        if stderr and stderr.decode().find('std::bad_alloc') != -1:
            status = 'MLE'
        else:
            status = 'UNK'
    else:
        status = 'UNK'
    return status

async def get_problem(problem_id: str) -> dict:

    """returns the problem dict according to the id"""

    PROBLEMS_DIR = os.path.join(os.curdir, 'problems')
    problem_path = os.path.join(PROBLEMS_DIR, f'{problem_id}.json')
    async with aiofiles.open(problem_path, 'r', encoding='utf-8') as f:
        content = await f.read()
    prob_dict = json.loads(content)
    return prob_dict

async def run_with_limit(
    submission_id: str,
    language: str,
    lan_config: dict,
    input: str,
    output: str, 
    time_limit: float, 
    memory_limit: int,
) -> tuple[str, float, int]:
    
    """create the run code subprocess with limits.
    
    This function creates the run code subprocess with time and memory limit.

    Args:
        submission_id (str): the id of the submission
        language (str): the language used in this submission
        lan_config (dict): the language configuration of the language
        input (str): the input of the corresponding test case
        output (str): the output of the corresponding test case
        time_limit (float): the time limit of the problem (in seconds)
        memory_limit (int): the memory limit of the problem (in MB)

    Returns:
        result_status (str): AC, WA, RE, TLE, MLE, UNK.
        used_time (float): the time used by this code (in seconds)
        used_memory (int): the memory used by this code (in MB)
    """

    # set the run command
    if language == 'python':
        ext = lan_config['file_ext']
        run_cmd = lan_config['run_cmd']
        src = f'./code{submission_id}.{ext}'
        cmd_str = run_cmd.format(src=src)
    else:
        exe = f'./code{submission_id}'
        run_cmd = lan_config['run_cmd']
        cmd_str = run_cmd.format(exe=exe)

    files = ', '.join(os.listdir(TMP_JUDGE_DIR))
    logs.queue_info_log(f'tmp now have {files}')
    logs.queue_info_log(f'running cmd {cmd_str}')
    cmd = cmd_str.split()
    # create the subprocess
    judge_process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=TMP_JUDGE_DIR,
        preexec_fn=judge_process_limits(time_limit, memory_limit)
    )

    stdout = None
    stderr = None
    returncode = None
    max_memory = 0
    judge_pid = judge_process.pid

    async def monitor_memory() -> None:

        """a function monitor the process' physical memory"""

        nonlocal max_memory
        process = psutil.Process(judge_pid)
        try:
            while process.is_running():
                # change the rss into MB
                current_memory = process.memory_info().rss / 1024 ** 2
                max_memory = max(max_memory, current_memory)
                if max_memory > memory_limit:
                    # kill the process
                    process.kill()
                await asyncio.sleep(0.05)
        except psutil.NoSuchProcess:
            # the process is already over
            return
        
    start_time = time.time()
    duration = None

    try:
        # activate the monitor tasks and the subprocess
        monitor_task = asyncio.create_task(monitor_memory())
        stdout, stderr = await asyncio.wait_for(
            judge_process.communicate(input.encode()),
            timeout=time_limit, # this will control the time and see if the code exceeds time limit
        )
        duration = time.time() - start_time
        returncode = await judge_process.wait()
        monitor_task.cancel()
    except asyncio.TimeoutError:
        # exceeds the time limit
        assert judge_process is not None # the TimeoutError has to be triggered after the process is created
        judge_process.terminate()
        duration = time.time() - start_time
        returncode = await judge_process.wait()
    finally:
        assert returncode is not None # needs the return code for judging
        assert duration is not None # needs the duration for the log
        status = analyze_run_results(output, returncode, stdout, stderr)
        return status, duration, int(max_memory)
    
async def judge_code(
    submission_id: str,
    language: str,
    languages: dict[str, Any],
    problem_id: str,
    code: str,
) -> list[tuple[str, float, int]]:
    
    """a function judges the code"""

    # create the tmp file for judge
    lan_config = languages[language]
    ext = lan_config['file_ext']
    file_name = f'code{submission_id}.{ext}'
    async with aiofiles.open(os.path.join(TMP_JUDGE_DIR, file_name), 'w', encoding='utf-8') as f:
        await f.write(code)

    # get the problem
    problem = await get_problem(problem_id)
    samples: list[dict] = problem['samples']

    # compile the code
    compile_retuncode = await compile(submission_id, lan_config)
    if compile_retuncode != 0:
        # compile error, remove the source file
        os.remove(os.path.join(TMP_JUDGE_DIR, file_name))
        return [('CE', 0.0, 0)] * len(samples)
    
    # judge the code
    if problem.get('time_limit') is not None:
        time_limit = problem['time_limit']
    else:
        time_limit = languages['time_limit']
    if problem.get('memory_limit') is not None:
        memory_limit = problem['memory_limit']
    else:
        memory_limit = languages['memory_limit']
    status_list = []
    for sample in samples:
        status = await run_with_limit(
            submission_id=submission_id,
            language=language,
            lan_config=lan_config,
            input=sample['input'],
            output=sample['output'],
            time_limit=time_limit,
            memory_limit=memory_limit,
        )
        status_list.append(status)

    # remove the judge file
    os.remove(os.path.join(TMP_JUDGE_DIR, file_name))
    if os.path.exists(os.path.join(TMP_JUDGE_DIR, f'code{submission_id}')):
        os.remove(os.path.join(TMP_JUDGE_DIR, f'code{submission_id}'))

    return status_list

def get_score_counts_logs(results: list[tuple[str, float, int]]) -> tuple[int, int, list[SubmissionTestDetail]]:

    """get the score, counts, and logs from the result list"""

    counts = 10 * len(results)
    score = 0
    submission_logs = []
    for i in range(len(results)):
        submission_logs.append(
            SubmissionTestDetail(
                sample_id=i + 1,
                result=results[i][0],
                time=results[i][1],
                memory=results[i][2],
            )
        )
        if results[i][0] == 'AC':
            score += 10
    return score, counts, submission_logs
