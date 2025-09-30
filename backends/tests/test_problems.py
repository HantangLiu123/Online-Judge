import unittest
import requests
from pydantic import ValidationError
from tortoise import Tortoise
from . import utils
from .settings import TORTOISE_ORM
from .user import User
from .test_schemas import ProblemList, ProblemSchemaUser
from shared.schemas import UserCredentials, ProblemSchema

default_admin = User(1, 'admin', 'admin')
test_user_1 = User(2, 'test_user_1', 'test_user_1')

class TestProblemEndpoints(unittest.IsolatedAsyncioTestCase):

    """testing all problems endpoints"""

    async def asyncSetUp(self) -> None:

        """init for the testing environment"""

        await Tortoise.init(TORTOISE_ORM)
        await utils.delete_all_users()
        await utils.clear_problems()
        await utils.user_factory(
            user_credential=UserCredentials(
                username=test_user_1.username,
                password=test_user_1.password,
            ),
            role='user',
            user_id=test_user_1.id
        )
        await utils.init_problems()

    async def asyncTearDown(self) -> None:
        
        """destory all data"""

        await utils.clear_problems()
        await utils.delete_all_users()
        await Tortoise.close_connections()

    def test_problem_list(self):

        """test the get problem list endpoint"""

        # wrong format -> bad request
        response = test_user_1.get_problem_list(2, 20, 'extra hard')
        self.assertEqual(response.status_code, requests.codes.bad_request)

        # page is too large -> not found
        response = test_user_1.get_problem_list(2, 20)
        self.assertEqual(response.status_code, requests.codes.not_found)

        # format is correct -> ok
        response = test_user_1.get_problem_list(1, 20)
        self.assertEqual(response.status_code, requests.codes.ok)

        # check for the format
        try:
            parsed_response = ProblemList(**response.json()['data'])
        except ValidationError:
            self.fail('The format of the problem list is incorrect')

    def test_get_problem(self):

        """test the get problem endpoint"""

        test_user_1.login()

        # cannot find the problem -> not found
        response = test_user_1.get_problem('p050')
        self.assertEqual(response.status_code, requests.codes.not_found)

        # getting the problem as a user
        response = test_user_1.get_problem('p001')
        self.assertEqual(response.status_code, requests.codes.ok)
        try: 
            parsed_response = ProblemSchemaUser(**response.json()['data'])
        except ValidationError:
            self.fail("The format of user's get problem is incorrect")

        # getting the problem as an adim
        default_admin.login()
        response = default_admin.get_problem('p001')
        try:
            parsed_response = ProblemSchema(**response.json()['data'])
        except ValidationError:
            self.fail("The format of admin's get problem is incorrect")

        test_user_1.logout()
        default_admin.logout()

    async def test_create_problem(self):

        """test the create problem endpoint"""

        PROBLEM = utils.get_problem_dict('p021.json')
        PROBLEM_WRONG_FORMAT = utils.get_problem_dict('p021_wrong_format.json')
        PROBLEM_CONFLICT_ID = utils.get_problem_dict('p021_conflict_id.json')

        # not logged in -> unauthorized
        response = test_user_1.create_problem(PROBLEM_WRONG_FORMAT)
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # wrong format -> bad request
        test_user_1.login()
        response = test_user_1.create_problem(PROBLEM_WRONG_FORMAT)
        self.assertEqual(response.status_code, requests.codes.bad_request)

        # conflict id -> conflict
        response = test_user_1.create_problem(PROBLEM_CONFLICT_ID)
        self.assertEqual(response.status_code, requests.codes.conflict)

        # correct format and id -> ok
        response = test_user_1.create_problem(PROBLEM)
        self.assertEqual(response.status_code, requests.codes.ok)
        self.assertTrue(await utils.problem_exist(PROBLEM['id']))

        test_user_1.logout()

    async def test_delete_problem(self):

        """test the delete problem endpoint"""

        # not logged in -> unauthorized
        response = test_user_1.delete_problem('p050')
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # not an admin -> forbidden
        test_user_1.login()
        response = test_user_1.delete_problem('p050')
        self.assertEqual(response.status_code, requests.codes.forbidden)

        # cannot find the problem -> not found
        default_admin.login()
        response = default_admin.delete_problem('p050')
        self.assertEqual(response.status_code, requests.codes.not_found)

        # delete success -> ok
        response = default_admin.delete_problem('p001')
        self.assertEqual(response.status_code, requests.codes.ok)
        self.assertFalse(await utils.problem_exist('p001'))

        test_user_1.logout()
        default_admin.logout()

if __name__ == "__main__":
    unittest.main()
