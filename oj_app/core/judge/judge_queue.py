import asyncio
import json
import uuid
import traceback
from datetime import datetime, timedelta
from redis import asyncio as aioredis
from oj_app.models.schemas import SubmissionPostModel, SubmissionResult
from ..submission.SubmissionResManager import submissionResultManager
from ..submission.TestLogManager import testLogManager
from ..submission.ResolveManager import resolveManager
from ..security.UserManager import userManager
from ..config import logs
from . import judge

class JudgeQueue:

    """a class for managing the judging queue"""

    def __init__(self, redis: aioredis.Redis, max_workers: int) -> None:
        self.redis = redis
        self.max_workers = max_workers
        self.running_tasks: dict[str, str] = {}
        self.is_running = False
        self.task_semasphore = asyncio.Semaphore(max_workers)
        self.languages = {}

    def set_languages(self, new_lan_settings: dict) -> None:

        """change or init the language settings"""

        self.languages = new_lan_settings

    async def enqueue_judge_task(
        self,
        judge_data: SubmissionPostModel,
        user_id: int,
    ) -> str:
        
        """put the new judge task into the queue"""

        # create the submission result and store in the database
        while True:
            submission_id = str(uuid.uuid4())
            submission = SubmissionResult(
                submission_id=submission_id,
                submission_time=datetime.now(),
                user_id=user_id,
                problem_id=judge_data.problem_id,
                language=judge_data.language,
                status='pending',
                code=judge_data.code,
            )
            if await submissionResultManager.insert_submission(submission):
                break

        # create the task and put into queue
        task = {
            'type': 'judge',
            'submission_id': submission_id,
            'problem_id': judge_data.problem_id,
            'user_id': str(user_id),
            'language': judge_data.language,
            'code': judge_data.code,
        }
        await self.redis.lpush('judge_queue', json.dumps(task)) # type: ignore

        # record the submission time for the user (for limiting submission rate)
        await self.redis.lpush(
            f'user_submission_timestamp:{user_id}',
            submission.submission_time.isoformat(),
        ) # type: ignore

        # record in the log
        message = f'task/submission{submission_id} created and moved into queue'
        logs.queue_info_log(message)

        return submission_id

    def _within_a_minute(self, now: datetime, past: bytes | None) -> bool:

        """helper funciton for allow_to_submit to calculate the condition of within a minute"""

        if past is None:
            return True
        return now - datetime.fromisoformat(past.decode()) < timedelta(minutes=1)

    async def allow_to_submit(self, user_id: int) -> bool:

        """return true or false according to the user's rate of submission.
        
        This function limits the rate of submission of a user within three times a minute.
        """

        now = datetime.now()
        while not self._within_a_minute(
            now,
            await self.redis.lindex(f'user_submission_timestamp:{user_id}', -1), # type: ignore
        ):
            await self.redis.rpop(f'user_submission_timestamp:{user_id}') # type: ignore
        return await self.redis.llen(f'user_submission_timestamp:{user_id}') < 3 # type: ignore
    
    async def _process_judge(self, task: dict[str, str], worker_name: str) -> None:

        """process a task, only used in workers"""

        task_id = task['submission_id']
        self.running_tasks[task_id] = worker_name
        message = f'{worker_name} is judging on submission{task_id}'
        logs.queue_info_log(message)

        try:
            # judge the code and analyze the result
            results = await judge.judge_code(
                submission_id=task_id,
                language=task['language'],
                languages=self.languages,
                problem_id=task['problem_id'],
                code=task['code'],
            )
            score, counts, submission_logs = judge.get_score_counts_logs(results)

            # store the results
            await submissionResultManager.update_submission(
                submission_id=task_id,
                status='success',
                score=score,
                counts=counts,
            )
            await testLogManager.insert_logs(
                submission_id=task_id,
                test_logs=submission_logs,
            )
            await self._update_resolve_relation(
                user_id=int(task['user_id']),
                problem_id=task['problem_id'],
                language=task['language'],
                score=score,
                counts=counts,
            )
            message = f'completing judging submission{task_id} and storing it into the database'
            logs.queue_info_log(message)
        except Exception as e:
            # record the failed judge
            await submissionResultManager.update_submission(
                submission_id=task_id,
                status='error',
            )
            tb_str = traceback.format_exc()
            message = f'Catching the exception: {str(e)} when judging submission{task_id}. Traceback: {tb_str}'
            logs.queue_error_log(message)
        finally:
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]

    async def enqueue_rejudge(self, submission_id: str) -> None:

        """add a rejudge task into the queue"""

        # construct the task
        old_submission = await submissionResultManager.get_submission_by_id(submission_id)
        if old_submission is None:
            raise ValueError('cannot find the submission with the id')
        task = {
            'type': 'rejudge',
            'submission_id': submission_id,
            'problem_id': old_submission['problem_id'],
            'user_id': str(old_submission['user_id']),
            'language': old_submission['language'],
            'code': old_submission['code'],
        }

        # put it into the queue, and change the status to pending
        await self.redis.lpush('judge_queue', json.dumps(task)) # type: ignore
        await submissionResultManager.update_submission(
            submission_id=submission_id,
            status='pending',
        )

        # record the log
        message = f'adding rejudge/submission{submission_id} into the queue'
        logs.queue_info_log(message)

    async def _process_rejudge(self, task: dict[str, str], worker_name: str) -> None:

        """process a rejudge task"""

        task_id = task['submission_id']
        self.running_tasks[task_id] = worker_name
        message = f'{worker_name} is rejudging on submission{task_id}'
        logs.queue_info_log(message)

        try:
            # judge the code and analyze the result
            results = await judge.judge_code(
                submission_id=task_id,
                language=task['language'],
                languages=self.languages,
                problem_id=task['problem_id'],
                code=task['code'],
            )
            score, counts, submission_logs = judge.get_score_counts_logs(results)

            # store the results
            await submissionResultManager.update_submission(
                submission_id=task_id,
                status='success',
                score=score,
                counts=counts,
            )
            await self._update_resolve_relation(
                user_id=int(task['user_id']),
                problem_id=task['problem_id'],
                language=task['language'],
                score=score,
                counts=counts,
            )
            if await testLogManager.get_log(task_id, 1) is None:
                # the old submission result does not have logs due to some reasons
                await testLogManager.insert_logs(
                    submission_id=task_id,
                    test_logs=submission_logs,
                )
            else:
                # just update the logs
                await testLogManager.change_logs(
                    submission_id=task_id,
                    new_logs=submission_logs,
                )
            message = f'completing judging submission{task_id} and storing it into the database'
            logs.queue_info_log(message)
        except Exception as e:
            # record the failed judge
            await submissionResultManager.update_submission(
                submission_id=task_id,
                status='error',
            )
            tb_str = traceback.format_exc()
            message = f'Catching the exception: {str(e)} when judging submission{task_id}. Traceback: {tb_str}'
            logs.queue_error_log(message)
        finally:
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]

    async def _update_resolve_relation(
        self,
        user_id: int,
        problem_id: str,
        language: str,
        score: int,
        counts: int,
    ) -> None:
        
        """update the resolve relation according to the score, counts, and past relation"""

        past_rel = await resolveManager.find_resolve_relation(problem_id, user_id, language)
        if past_rel:
            # already resolved, nothing to update
            return
        elif past_rel is None:
            # no records
            new_status = score == counts
            await resolveManager.insert_relation(problem_id, user_id, language, new_status)
            if new_status:
                # the problem is resolved
                await userManager.add_resolve_count(user_id)
        else:
            # need to update the relation
            new_status = score == counts
            if not new_status:
                # still not resolved
                return
            else:
                await resolveManager.update_relation(problem_id, user_id, language, new_status)
                # adding the resolve count for the user
                await userManager.add_resolve_count(user_id)

    async def _get_next_task(self) -> dict[str, str] | None:

        """getting the next task"""

        task_data = await self.redis.rpop('judge_queue') # type: ignore
        if task_data:
            return json.loads(task_data) # type: ignore
        return None

    async def _worker(self, worker_id: int) -> None:

        """coroutine for process each task"""

        worker_name = f'worker_{worker_id}'

        while self.is_running:
            task = await self._get_next_task()
            if task:
                if task['type'] == 'judge':
                    async with self.task_semasphore:
                        await self._process_judge(task, worker_name)
                else:
                    async with self.task_semasphore:
                        await self._process_rejudge(task, worker_name)
            else:
                await asyncio.sleep(0.5)

    async def start(self):

        """start the queue system"""

        if self.is_running:
            return
        
        self.is_running = True
        logs.queue_info_log(f'Starting queue with max {self.max_workers} concurrent tasks')

        # the worker coroutines are slightly more than the max_workers 
        workers_count = self.max_workers + 2
        self.workers = [asyncio.create_task(self._worker(i)) for i in range(workers_count)]

    async def stop(self):

        """stop the queue system"""

        if not self.is_running:
            return
        
        self.is_running = False
        await asyncio.gather(*self.workers)

        # cancel all coroutines that refuce to close
        for task in self.running_tasks:
            worker_id = int(self.running_tasks[task][-1])
            self.workers[worker_id].cancel()

        logs.queue_info_log(f'Closed the queue')

    async def flush_redis(self):

        """flush the redis database"""

        await self.redis.flushdb()
