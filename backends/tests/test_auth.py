import unittest
import requests
from tortoise import Tortoise
from pydantic import ValidationError
from . import utils
from .user import User
from .test_schemas import LoginResponse
from shared.schemas import UserCredentials
from .settings import TORTOISE_ORM

test_user = User(2, 'test_user_1', 'test_user_1')
test_user_wrong_format = User(2, 'test_user_1', '')
test_user_wrong_password = User(2, 'test_user_1', '123456')

class TestAuthEndpoints(unittest.IsolatedAsyncioTestCase):

    """tests all authorization endpoints"""

    async def asyncSetUp(self) -> None:
        await Tortoise.init(TORTOISE_ORM)
        await utils.delete_all_users()

    async def test_login(self):

        """test the login endpoint"""

        # create a banned user
        await utils.user_factory(UserCredentials(
            username=test_user.username,
            password=test_user.password,
        ), 'banned', test_user.id)

        # incorrect format -> bad request
        response = test_user_wrong_format.login()
        self.assertEqual(response.status_code, requests.codes.bad_request)

        # wrong password -> unauthorized
        response = test_user_wrong_password.login()
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # banned -> forbidden
        response = test_user.login()
        self.assertEqual(response.status_code, requests.codes.forbidden)

        # change the user role
        await utils.change_user_role(test_user.username, 'user')

        # login success -> ok
        response = test_user.login()
        self.assertEqual(response.status_code, requests.codes.ok)
        login_response = response.json()['data']
        try:
            parsed_response = LoginResponse(**login_response)
        except ValidationError:
            self.fail()

        test_user.logout()
        await utils.user_destroy(test_user.username)

    async def test_logout(self):

        # create a user
        await utils.user_factory(UserCredentials(
            username=test_user.username,
            password=test_user.password,
        ), 'user', test_user.id)

        # has not logged in -> unauthorized
        response = test_user.logout()
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # logout success -> ok
        response = test_user.login()
        self.assertEqual(response.status_code, requests.codes.ok)
        response = test_user.logout()
        self.assertEqual(response.status_code, requests.codes.ok)

        await utils.user_destroy(test_user.username)

    async def asyncTearDown(self) -> None:
        await Tortoise.close_connections()

if __name__ == "__main__":
    unittest.main()
