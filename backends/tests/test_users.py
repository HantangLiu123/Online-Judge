import unittest
import requests
from pydantic import ValidationError
from tortoise import Tortoise
from .settings import TORTOISE_ORM
from .user import User
from . import utils
from . test_schemas import UserSignIn, CreateAdmin, UserInfo, ChangeRole, UserList

# the 10 users already added
users = [User(i + 1, f'test_user_{i}', f'test_user_{i}') for i in range(1, 11)]
default_admin = User(1, 'admin', 'admin')

class TestUserEndpoints(unittest.IsolatedAsyncioTestCase):

    """test all users endpoints"""

    async def asyncSetUp(self) -> None:
        await Tortoise.init(TORTOISE_ORM)
        await utils.delete_all_users()

        # add 10 users for test
        await utils.test_init_small()

    async def asyncTearDown(self) -> None:
        await utils.delete_all_users()
        await Tortoise.close_connections()

    def test_sign_in(self):

        """test the sign in endpoint"""

        new_user = User(12, 'test_user_11', 'test_user_11')
        new_user_wrong_format = User(12, 'test_user_11', '')

        # wrong format -> bad request
        response = User.sign_in_new_user(new_user_wrong_format.username, new_user_wrong_format.password)
        self.assertEqual(response.status_code, requests.codes.bad_request)

        # username already exists -> bad request
        response = User.sign_in_new_user(users[0].username, users[0].password)
        self.assertEqual(response.status_code, requests.codes.bad_request)

        # correct format -> success
        response = User.sign_in_new_user(new_user.username, new_user.password)
        self.assertEqual(response.status_code, requests.codes.ok)

        # check the format of the response data
        response_data = response.json()['data']
        try:
            parsed_data = UserSignIn(**response_data)
        except ValidationError:
            self.fail('The response format of user sign in is incorrect')

    def test_new_admin(self):

        """test the admin sign in endpoint"""

        new_admin = User(12, 'test_admin', 'test_admin')
        new_admin_wrong_format = User(12, 'test_admin', '')

        # not logged in -> unauthorized
        response = users[0].create_admin(new_admin_wrong_format.username, new_admin_wrong_format.password)
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # wrong format -> bad request
        users[0].login()
        response = users[0].create_admin(new_admin_wrong_format.username, new_admin_wrong_format.password)
        self.assertEqual(response.status_code, requests.codes.bad_request)

        # not an admin -> forbidden
        response = users[0].create_admin(new_admin.username, new_admin.password)
        self.assertEqual(response.status_code, requests.codes.forbidden)

        # correct format and user -> ok
        default_admin.login()
        response = default_admin.create_admin(new_admin.username, new_admin.password)
        self.assertEqual(response.status_code, requests.codes.ok)

        # check the format
        response_data = response.json()['data']
        try:
            parsed_data = CreateAdmin(**response_data)
        except ValidationError:
            self.fail('The response format of the admin sign in endpoint is incorrect')

        users[0].logout()
        default_admin.logout()

    def test_get_user(self):

        """test the user info endpoint"""

        # not logged in -> unauthorized
        response = users[0].get_user_info(users[1].id)
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # not checking the id of him/herself -> forbidden
        users[0].login()
        response = users[0].get_user_info(users[1].id)
        self.assertEqual(response.status_code, requests.codes.forbidden)

        # checking him/herself -> ok
        response = users[0].get_user_info(users[0].id)
        self.assertEqual(response.status_code, requests.codes.ok)

        # check the response format
        response_data = response.json()['data']
        try:
            parsed_data = UserInfo(**response_data)
        except ValidationError:
            self.fail('The response format of user info endpoint is incorrect')

        # cannot find the user -> not found
        default_admin.login()
        response = default_admin.get_user_info(50)
        self.assertEqual(response.status_code, requests.codes.not_found)

        # a user exists -> ok
        response = default_admin.get_user_info(users[0].id)
        self.assertEqual(response.status_code, requests.codes.ok)

        # check the format
        response_data = response.json()['data']
        try:
            parsed_data = UserInfo(**response_data)
        except ValidationError:
            self.fail('The response format of user info endpoint is incorrect')

        users[0].logout()
        default_admin.logout()

    def test_change_user_role(self):

        """test the change role endpoint"""

        # not logged in -> unauthorized
        response = users[0].change_user_role(50, 'qwer')
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # wrong format -> bad request
        users[0].login()
        response = users[0].change_user_role(50, 'qwer')
        self.assertEqual(response.status_code, requests.codes.bad_request)

        # not an admin -> forbidden
        response = users[0].change_user_role(50, 'banned')
        self.assertEqual(response.status_code, requests.codes.forbidden)

        # cannot find the target user -> not found
        default_admin.login()
        response = default_admin.change_user_role(50, 'banned')
        self.assertEqual(response.status_code, requests.codes.not_found)

        # correct format by an admin of an existed user -> ok
        response = default_admin.change_user_role(users[1].id, 'banned')
        self.assertEqual(response.status_code, requests.codes.ok)

        # check the format
        response_data = response.json()['data']
        try:
            parsed_response = ChangeRole(**response_data)
        except ValidationError:
            self.fail('the response format of change role endpoint is incorrect')

        users[0].logout()
        default_admin.logout()

    def test_user_list(self):

        """test the user list endpoint"""

        # not logged in -> unauthorized
        response = users[0].get_user_list(2, 20)
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # wrong format -> bad request
        users[0].login()
        response = users[0].get_user_list(-1, -1)
        self.assertEqual(response.status_code, requests.codes.bad_request)

        # not an admin -> forbidden
        response = users[0].get_user_list(2, 20)
        self.assertEqual(response.status_code, requests.codes.forbidden)

        # the page number is too large -> not found
        default_admin.login()
        response = default_admin.get_user_list(2, 20)
        self.assertEqual(response.status_code, requests.codes.not_found)

        # correct format by an admin -> ok
        response = default_admin.get_user_list(1, 20)
        self.assertEqual(response.status_code, requests.codes.ok)

        # check the format
        response_data = response.json()['data']
        try:
            parsed_response = UserList(**response_data)
        except ValidationError:
            self.fail('The response format of the user list is incorrect')

        users[0].logout()
        default_admin.logout()

if __name__ == "__main__":
    unittest.main()
