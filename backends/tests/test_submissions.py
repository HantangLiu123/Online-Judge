import unittest
import requests
import time
from datetime import datetime
from redis import asyncio as aioredis
from tortoise import Tortoise
from pydantic import ValidationError
from .settings import TORTOISE_ORM
from . import utils
from .user import User
from .test_schemas import GetSubmissionResponse, SubmissionLogResponse, SubmissionList, SubmissionResponse
from shared.schemas import UserCredentials, SubmissionData, SubmissionTestDetail

default_admin = User(1, 'admin', 'admin')
test_user_1 = User(2, 'test_user_1', 'test_user_1')

LEGAL_SUBMISSION_AC = {
    'problem_id': 'p001',
    'language': 'python',
    'code': """
n = int(input())
nums = list(map(int, input().split()))
target = int(input())

num_map = {}
for i, num in enumerate(nums):
    complement = target - num
    if complement in num_map:
        print(num_map[complement], i)
        break
    num_map[num] = i
""",
}

LEGAL_SUBMISSION_RE = {
    'problem_id': 'p001',
    'language': 'python',
    'code': """
n = 1 / 0
""",
}

LEGAL_SUBMISSION_TLE = {
    'problem_id': 'p001',
    'language': 'python',
    'code': """
import time
time.sleep(5)
""",
}

ILLEGAL_SUBMISSION = {
    'problem_id': 'p001',
    'language': 'python',
}

SUBMISSION_DATA_USER = SubmissionData(
    submission_id='9bfe5ec9-a270-4e25-bb53-afeda9c123a2',
    submission_time=datetime.now(),
    user_id=2,
    problem_id='p001',
    language='python',
    status='success',
    code="""
n = int(input())
nums = list(map(int, input().split()))
target = int(input())

num_map = {}
for i, num in enumerate(nums):
    complement = target - num
    if complement in num_map:
        print(num_map[complement], i)
        break
    num_map[num] = i
""",
    score=30,
    counts=30,
    details=[
        SubmissionTestDetail(test_id=1, result='AC', time=0, memory=1),
        SubmissionTestDetail(test_id=2, result='AC', time=0, memory=1),
        SubmissionTestDetail(test_id=3, result='AC', time=0, memory=1),
    ],
)

SUBMISSION_DATA_ADMIN = SubmissionData(
    submission_id='186919bc-e3d0-408b-b4c1-f7e2af69e9fa',
    submission_time=datetime.now(),
    user_id=1,
    problem_id='p001',
    language='python',
    status='success',
    code="""
n = int(input())
nums = list(map(int, input().split()))
target = int(input())

num_map = {}
for i, num in enumerate(nums):
    complement = target - num
    if complement in num_map:
        print(num_map[complement], i)
        break
    num_map[num] = i
""",
    score=20,   # intentionally mistake for rejudge
    counts=30,
    details=[
        SubmissionTestDetail(test_id=1, result='RE', time=0, memory=1),  # intentionally mistake for rejudge
        SubmissionTestDetail(test_id=2, result='AC', time=0, memory=1),
        SubmissionTestDetail(test_id=3, result='AC', time=0, memory=1),
    ],
)

class TestSubmissionEndpoints(unittest.IsolatedAsyncioTestCase):

    """test all submission endpoints"""

    async def asyncSetUp(self) -> None:

        """init the testing environment"""

        await Tortoise.init(TORTOISE_ORM)
        self.redis = await aioredis.from_url('redis://localhost:6379/0')
        await utils.clear_languages(self.redis)
        await utils.clear_problems()
        await utils.delete_all_users()
        await utils.clear_user_submission_timestamp(self.redis)
        await utils.init_languages(self.redis)
        await utils.user_factory(
            UserCredentials(
                username='test_user_1',
                password='test_user_1',
            ),
            'user',
            2,
        )
        await utils.init_problems()

    async def asyncTearDown(self) -> None:
        
        """remove info from database"""

        if not hasattr(self, 'redis'):
            self.redis = await aioredis.from_url('redis://localhost:6379/0')

        await utils.clear_languages(self.redis)
        await utils.clear_problems()
        await utils.delete_all_users()
        await utils.clear_user_submission_timestamp(self.redis)
        await self.redis.close()
        await self.redis.connection_pool.disconnect() # type: ignore
        await Tortoise.close_connections()

    async def test_a_get_submission(self):

        """test the get submission endpoint"""

        await utils.submission_factory(SUBMISSION_DATA_USER)
        await utils.submission_factory(SUBMISSION_DATA_ADMIN)
        test_user_1.logout()
        
        # not logged in -> unauthorized
        response = test_user_1.get_submission('no such id')
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # cannot find -> not found
        test_user_1.login()
        response = test_user_1.get_submission('no such id')
        self.assertEqual(response.status_code, requests.codes.not_found)

        # user getting other's submission -> forbidden
        response = test_user_1.get_submission(SUBMISSION_DATA_ADMIN.submission_id)
        self.assertEqual(response.status_code, requests.codes.forbidden)

        # user getting his/her submission -> success
        response = test_user_1.get_submission(SUBMISSION_DATA_USER.submission_id)
        self.assertEqual(response.status_code, requests.codes.ok)
        try:
            parsed_response = GetSubmissionResponse(**response.json()['data'])
        except ValidationError:
            self.fail('the format of the get submission endpoint is incorrect')

        test_user_1.logout()

    async def test_b_get_submission_log(self):

        """test the get submission log endpoint"""

        await utils.submission_factory(SUBMISSION_DATA_USER)
        await utils.submission_factory(SUBMISSION_DATA_ADMIN)
        test_user_1.logout()
        
        # not logged in -> unauthorized
        response = test_user_1.get_submission_log('no such id')
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # cannot find -> not found
        test_user_1.login()
        response = test_user_1.get_submission_log('no such id')
        self.assertEqual(response.status_code, requests.codes.not_found)

        # user getting other's submission -> forbidden
        response = test_user_1.get_submission_log(SUBMISSION_DATA_ADMIN.submission_id)
        self.assertEqual(response.status_code, requests.codes.forbidden)

        # user getting his/her submission -> success
        response = test_user_1.get_submission_log(SUBMISSION_DATA_USER.submission_id)
        self.assertEqual(response.status_code, requests.codes.ok)
        try:
            parsed_response = SubmissionLogResponse(**response.json()['data'])
        except ValidationError:
            self.fail('the format of the get submission log endpoint is incorrect')

        test_user_1.logout()

    async def test_c_get_submission_list(self):

        """test the get submission list endpoint"""

        await utils.submission_factory(SUBMISSION_DATA_USER)
        await utils.submission_factory(SUBMISSION_DATA_ADMIN)
        default_admin.logout()
        test_user_1.logout()

        # not logged in -> unauthorized
        response = test_user_1.get_submission_list(problem_id='p001')
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # wrong parameters -> bad request
        test_user_1.login()
        response = test_user_1.get_submission_list()
        self.assertEqual(response.status_code, requests.codes.bad_request)

        # logged in, should only get one result
        response = test_user_1.get_submission_list(problem_id='p001')
        self.assertEqual(response.status_code, requests.codes.ok)
        try:
            parsed_response = SubmissionList(**response.json()['data'])
            self.assertEqual(parsed_response.total, 1)
        except ValidationError:
            self.fail('The format of the submission list is incorrect')

        # the admin should get two results
        default_admin.login()
        response = default_admin.get_submission_list(problem_id='p001')
        self.assertEqual(response.status_code, requests.codes.ok)
        try:
            parsed_response = SubmissionList(**response.json()['data'])
            self.assertEqual(parsed_response.total, 2)
        except ValidationError:
            self.fail('The format of the submission list is incorrect')

        default_admin.logout()
        test_user_1.logout()

    async def test_d_submit_endpoint(self):

        """test the submit endpoint"""

        test_user_1.logout()

        # not logged in -> unauthorized
        response = test_user_1.submit_code(**ILLEGAL_SUBMISSION)
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # illegal params -> bad request
        test_user_1.login()
        response = test_user_1.submit_code(**ILLEGAL_SUBMISSION)
        self.assertEqual(response.status_code, requests.codes.bad_request)

        # legal submission -> ok for the first three, too many requests for the 4th
        try:
            response = test_user_1.submit_code(**LEGAL_SUBMISSION_RE)
            self.assertEqual(response.status_code, requests.codes.ok)
            parsed_re_response = SubmissionResponse(**response.json()['data'])

            response = test_user_1.submit_code(**LEGAL_SUBMISSION_TLE)
            self.assertEqual(response.status_code, requests.codes.ok)
            parsed_tle_response = SubmissionResponse(**response.json()['data'])

            response = test_user_1.submit_code(**LEGAL_SUBMISSION_AC)
            self.assertEqual(response.status_code, requests.codes.ok)
            parsed_ac_response = SubmissionResponse(**response.json()['data'])

            response = test_user_1.submit_code(**LEGAL_SUBMISSION_AC)
            self.assertEqual(response.status_code, requests.codes.too_many_requests)

            time.sleep(20)
            response = test_user_1.get_submission_log(parsed_re_response.submission_id)
            re_submission = SubmissionLogResponse(**response.json()['data'])
            self.assertEqual(re_submission.details[0].result, 'RE')

            response = test_user_1.get_submission_log(parsed_tle_response.submission_id)
            tle_submission = SubmissionLogResponse(**response.json()['data'])
            self.assertEqual(tle_submission.details[0].result, 'TLE')
            
            response = test_user_1.get_submission_log(parsed_ac_response.submission_id)
            ac_submission = SubmissionLogResponse(**response.json()['data'])
            self.assertEqual(ac_submission.details[0].result, 'AC')
        except ValidationError:
            self.fail('the format of the submit code endpoint is incorrect')

        test_user_1.logout()

    async def test_e_rejudge(self):

        """test the rejudge endpoint"""

        test_user_1.logout()
        default_admin.logout()
        await utils.submission_factory(SUBMISSION_DATA_ADMIN)

        # not logged in -> unauthorized
        response = test_user_1.rejudge_code(SUBMISSION_DATA_ADMIN.submission_id)
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # not an admin -> forbidden
        test_user_1.login()
        response = test_user_1.rejudge_code(SUBMISSION_DATA_ADMIN.submission_id)
        self.assertEqual(response.status_code, requests.codes.forbidden)

        # admin rejudge -> success
        default_admin.login()
        response = default_admin.rejudge_code(SUBMISSION_DATA_ADMIN.submission_id)
        self.assertEqual(response.status_code, requests.codes.ok)
        try:
            parsed_response = SubmissionResponse(**response.json()['data'])
        except ValidationError:
            self.fail('the format of the rejudge response is incorrect')

        time.sleep(20)

        response = default_admin.get_submission_log(SUBMISSION_DATA_ADMIN.submission_id)
        parsed_response = SubmissionLogResponse(**response.json()['data'])
        self.assertEqual(parsed_response.score, 30)
        self.assertEqual(parsed_response.details[0].result, 'AC')

        default_admin.logout()
        test_user_1.logout()

if __name__ == "__main__":
    unittest.main()
