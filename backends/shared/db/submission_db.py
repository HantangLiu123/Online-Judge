import asyncio
from datetime import datetime
from tortoise.exceptions import IntegrityError
from ..models import Submission, SubmissionStatus, Test
from ..schemas import SubmissionPostModel, SubmissionData, SubmissionTestDetail
from ..utils import submission_parse, oj_cache

async def create_submission_in_db(
    submission: SubmissionPostModel,
    submission_id: str,
    user_id: int,
    submission_time: datetime,
    status: SubmissionStatus,
    score: int | None = None,
    counts: int | None = None,
) -> bool:

    """create the submission in the database
    
    This function returns true if the process succeeds,
    return false if it fails
    """

    try:
        await Submission.create(
            submission_id=submission_id,
            user_id=user_id,
            problem_id=submission.problem_id,
            submission_time=submission_time,
            language=submission.language,
            status=status,
            score=score,
            counts=counts,
            code=submission.code,
        )
    except IntegrityError:
        return False
    
    # delete the cache
    await oj_cache.delete_cache(
        item_type='submission',
        user_id=user_id,
        problem_id=submission.problem_id,
    )
    return True

async def get_submission_in_db(submission_id: str):

    """get the submission by id"""

    submission = await Submission.get_or_none(submission_id=submission_id)
    if submission is None:
        return None, None
    tests = await submission.tests.order_by('test_id').all() # pyright: ignore[reportArgumentType]
    return submission, tests

async def update_submission_in_db(
    submission: Submission,
    status: SubmissionStatus,
    score: int | None,
    counts: int | None,
    tests: list[SubmissionTestDetail] | None,
):
    
    """update the submission in the database
    
    This function updates the submission in the database. For the tests,
    if the tests parameter is not None, the function will remove the old
    tests first, and then create the new tests.
    """

    submission.status = status
    submission.score = score # type: ignore
    submission.counts = counts # type: ignore
    if tests is not None:
        await submission.tests.all().delete() # type: ignore
        insert_tasks = [submission.tests.create(    # type: ignore
            id=test.id,
            result=test.result,
            time=test.time,
            memory=test.memory,
        ) for test in tests]
        await asyncio.gather(*insert_tasks)

    # delete the cache
    await oj_cache.delete_cache(item_type='submission', submission_id=submission.submission_id)

async def reset_submission_table():

    """reset the submission table"""

    await Submission.all().delete()

async def export_submission_table():

    """export the submission table from db"""

    return await Submission.all()

async def import_submission_to_db(submission_data: list[SubmissionData]):

    """import submissions into the database"""

    submissions: list[Submission] = []
    tests: list[Test] = []
    for data in submission_data:
        submission, tests_of_submission = submission_parse.parse_data_to_submission(data)
        submissions.append(submission)
        tests.extend(tests_of_submission)
    await Submission.bulk_create(submissions, ignore_conflicts=True)
    await Test.bulk_create(tests, ignore_conflicts=True)
