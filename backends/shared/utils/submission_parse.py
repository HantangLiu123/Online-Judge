from ..models import Submission, Test
from ..schemas import SubmissionData, SubmissionTestDetail

def parse_submission_to_data(submission: Submission):

    """parse the submission model into the submissiondata schema"""

    # create the test details
    tests: list[Test] = await submission.tests.all() # type: ignore
    test_details = []
    for test in tests:
        test_details.append(
            SubmissionTestDetail(
                id=test.test_id, 
                result=test.result,
                time=test.time,
                memory=test.memory,
            )
        )

    # parse to data
    return SubmissionData(
        submission_id=str(submission.submission_id),
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
        submission_id=submission_data.submission_id,
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
    tests = []
    for test in submission_data.details:
        tests.append(
            Test(
                test_id=test.id,
                submission=submission,
                result=test.result,
                time=test.time,
                memory=test.memory,
            )
        )

    return submission, tests
