from ..models import Submission, Test
from ..schemas import SubmissionData, SubmissionTestDetail

async def parse_submission_to_data(submission: Submission):

    """parse the submission model into the submissiondata schema"""

    # create the test details
    tests: list[Test] = await submission.tests.order_by('test_id').all() # type: ignore
    test_details = [SubmissionTestDetail(
        test_id=test.test_id, 
        result=test.result,
        time=test.time,
        memory=test.memory,
    ) for test in tests]

    # parse to data
    return SubmissionData(
        submission_id=str(submission.id),
        submission_time=submission.submission_time,
        user_id=submission.user_id, # type: ignore
        problem_id=submission.problem_id, # type: ignore
        language=submission.language,
        status=submission.status, # type: ignore
        score=submission.score,
        counts=submission.counts,
        code=submission.code,
        details=test_details,
    )

def parse_data_to_submission(submission_data: SubmissionData) -> tuple[Submission, list[Test]]:

    """parse the data schema to submission model"""

    # create the submission
    submission = Submission(
        id=submission_data.submission_id,
        submission_time=submission_data.submission_time,
        user_id=submission_data.user_id,
        problem_id=submission_data.problem_id,
        language=submission_data.language,
        status=submission_data.status,
        score=submission_data.score,
        counts=submission_data.counts,
        code=submission_data.code
    )

    # create the tests
    tests = [Test(
        test_id=test.test_id,
        submission_id=submission.id,
        result=test.result,
        time=test.time,
        memory=test.memory,
    ) for test in submission_data.details]

    return submission, tests
