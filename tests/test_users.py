import unittest
import requests
from redis import asyncio as aioredis
from pydantic import ValidationError
from user_test_functions import User
from test_models.user_schemas import (
    UserSignInResponse,
    AdminCreateResponse,
    UserInfoResponse,
    ChangeRoleResponse,
    UserListResponse,
)
import helper

REDIS_URL = 'redis://localhost:6379/0'
ADMIN = User('admin', 'admin')
ADMIN_ID = 1
TEST_USER_1 = User('test_user_1', 'test_user_1')
TEST_USER_1_ID = 2

class TestUserEndpoints(unittest.IsolatedAsyncioTestCase):

    """test case of all user endpoints"""

    async def asyncSetUp(self) -> None:
        
        """connect to the redis client, clear the cache"""

        self.redis = aioredis.from_url(REDIS_URL)
        await helper.clear_api_cache(self.redis)

    async def asyncTearDown(self) -> None:
        
        """disconnect the redis client"""

        if hasattr(self, 'redis') and self.redis:
            await self.redis.close()
            await self.redis.connection_pool.disconnect() # pyright: ignore[reportGeneralTypeIssues]

    def test_sign_in(self):

        """test the sign in endpoint"""

        # no password (wrong format) -> bad request
        response = User.sign_in_new_user('test_user_20', '')
        self.assertEqual(response.status_code, requests.codes.bad_request)

        # username conflict -> bad request
        response = User.sign_in_new_user('test_user_20', 'test_user_20')
        self.assertEqual(response.status_code, requests.codes.bad_request)

        # success -> ok, check the data and the user info in the database
        response = User.sign_in_new_user('test_user_21', 'test_user_21')
        self.assertEqual(response.status_code, requests.codes.ok)
        response_data = response.json()['data']
        try:
            parsed_response = UserSignInResponse(**response_data)
        except ValidationError:
            self.fail('the response format of user sign in endpoint is incorrect')

        new_user_id = parsed_response.user_id
        ADMIN.login()
        user_info_response = ADMIN.get_user_info(new_user_id)
        self.assertEqual(
            user_info_response.json()['data'],
            {
                'user_id': new_user_id,
                'username': 'test_user_21',
                'role': 'user',
            },
        )

        ADMIN.logout()

    def test_create_admin(self):

        """test the create admin endpoint"""

        # not logged in -> unauthorized
        response = TEST_USER_1.create_admin('admin', '')
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # not an admin -> forbidden
        TEST_USER_1.login()
        response = TEST_USER_1.create_admin('admin', '')
        self.assertEqual(response.status_code, requests.codes.forbidden)

        # format incorrect -> bad request
        ADMIN.login()
        response = ADMIN.create_admin('admin', '')
        self.assertEqual(response.status_code, requests.codes.bad_request)

        # username conflict -> bad request
        response = ADMIN.create_admin('admin', 'admin')
        self.assertEqual(response.status_code, requests.codes.bad_request)

        # success -> ok, check the response format and user info in the database
        response = ADMIN.create_admin('test_admin_1', 'test_admin_1')
        self.assertEqual(response.status_code, requests.codes.ok)
        response_data = response.json()['data']
        try:
            parsed_response = AdminCreateResponse(**response_data)
        except ValidationError:
            self.fail('the response format of create admin is incorrect')

        new_admin_id = parsed_response.user_id
        user_info_response = ADMIN.get_user_info(new_admin_id)
        self.assertEqual(
            user_info_response.json()['data'],
            {
                'user_id': new_admin_id,
                'username': 'test_admin_1',
                'role': 'admin',
            },
        )

        TEST_USER_1.logout()
        ADMIN.logout()

    def test_get_user_info(self):

        """test the user info endpoint"""

        # not logged in -> unauthorized
        response = TEST_USER_1.get_user_info(TEST_USER_1_ID)
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # success since checking itself
        TEST_USER_1.login()
        response = TEST_USER_1.get_user_info(TEST_USER_1_ID)
        self.assertEqual(response.status_code, requests.codes.ok)
        response_data = response.json()['data']
        try:
            parsed_result = UserInfoResponse(**response_data)
        except ValidationError:
            self.fail('the format of user info is incorrect')

        # failed since checking others -> forbidden
        response = TEST_USER_1.get_user_info(ADMIN_ID)
        self.assertEqual(response.status_code, requests.codes.forbidden)

        # failed for not finding the user -> not found
        ADMIN.login()
        response = ADMIN.get_user_info(50)
        self.assertEqual(response.status_code, requests.codes.not_found)

        # success
        response = ADMIN.get_user_info(TEST_USER_1_ID)
        self.assertEqual(response.status_code, requests.codes.ok)
        response_data = response.json()['data']
        try:
            parsed_result = UserInfoResponse(**response_data)
        except ValidationError:
            self.fail('the format of user info is incorrect')

        ADMIN.logout()
        TEST_USER_1.logout()

    def test_change_role(self):

        """test the change user role endpoint"""

        # not logged in -> unauthorized
        response = TEST_USER_1.change_user_role(TEST_USER_1_ID, 'illegal_role')
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # no enough authority (only admin can change role) -> forbidden
        TEST_USER_1.login()
        response = TEST_USER_1.change_user_role(TEST_USER_1_ID, 'illegal_role')
        self.assertEqual(response.status_code, requests.codes.forbidden)

        # format incorrect -> bad request
        ADMIN.login()
        response = ADMIN.change_user_role(TEST_USER_1_ID, 'illegal_role')
        self.assertEqual(response.status_code, requests.codes.bad_request)

        # success
        response = ADMIN.change_user_role(TEST_USER_1_ID, 'admin')
        self.assertEqual(response.status_code, requests.codes.ok)
        response_data = response.json()['data']
        try:
            parsed_response = ChangeRoleResponse(**response_data)
        except ValidationError:
            self.fail('the format of changing role is incorrect')

        # check the database for the change
        response = ADMIN.get_user_info(TEST_USER_1_ID)
        self.assertEqual(
            response.json()['data'],
            {
                'user_id': TEST_USER_1_ID,
                'username': 'test_user_1',
                'role': 'admin',
            },
        )

        ADMIN.change_user_role(TEST_USER_1_ID, 'user')
        ADMIN.logout()
        TEST_USER_1.logout()

    async def test_user_list(self):

        """test the get user list endpoint"""

        # not logged in -> unauthorized
        response = TEST_USER_1.get_user_list(page=50, page_size=33)
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # user cannot check user list -> forbidden
        TEST_USER_1.login()
        response = TEST_USER_1.get_user_list(page=50, page_size=33)
        self.assertEqual(response.status_code, requests.codes.forbidden)

        # the page_size is not correct -> bad request
        ADMIN.login()
        response = ADMIN.get_user_list(page=50, page_size=33)
        self.assertEqual(response.status_code, requests.codes.bad_request)

        # the page num is too big -> not found
        response = ADMIN.get_user_list(page=50, page_size=20)
        self.assertEqual(response.status_code, requests.codes.not_found)

        # success
        response = ADMIN.get_user_list(page=1, page_size=20)
        self.assertEqual(response.status_code, requests.codes.ok)
        response_data = response.json()['data']
        try:
            parsed_response = UserListResponse(**response_data)
        except ValidationError:
            self.fail('the format of the user list response is incorrect')

        # check the cache
        key_format = f"fastapi-cache:user_list:1:20:*"
        key_list = await helper.get_api_cache_keys(self.redis, key_format)
        if key_list == []:
            self.fail('the cache of user list failed')

        # change a user's role to fail the cache, and check it
        ADMIN.change_user_role(TEST_USER_1_ID, 'admin')
        key_list = await helper.get_api_cache_keys(self.redis, key_format)
        if key_list != []:
            self.fail('the cache deletion failed')

        ADMIN.change_user_role(TEST_USER_1_ID, 'user')
        ADMIN.logout()
        TEST_USER_1.logout()

if __name__ == "__main__":
    unittest.main()
