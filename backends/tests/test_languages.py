import unittest
import requests
from pydantic import ValidationError
from tortoise import Tortoise
from redis import asyncio as aioredis
from .user import User
from . import utils
from .settings import TORTOISE_ORM
from .test_schemas import LanList
from shared.schemas import UserCredentials

REDIS_URL = 'redis://localhost:6379/0'

default_admin = User(1, 'admin', 'admin')
test_user_1 = User(2, 'test_user_1', 'test_user_1')

class TestLanguagesEndpoints(unittest.IsolatedAsyncioTestCase):

    """test all language endpoints"""

    async def asyncSetUp(self) -> None:
        
        """init the testing environment"""

        await Tortoise.init(TORTOISE_ORM)
        self.redis = await aioredis.from_url('redis://localhost:6379/0')
        await utils.clear_languages(self.redis)
        await utils.delete_all_users()
        await utils.init_languages(self.redis)
        await utils.user_factory(
            UserCredentials(
                username='test_user_1',
                password='test_user_1',
            ),
            'user',
            2,
        )

    async def asyncTearDown(self) -> None:
        
        """remove info from database"""

        if not hasattr(self, 'redis'):
            self.redis = await aioredis.from_url('redis://localhost:6379/0')

        await utils.clear_languages(self.redis)
        await utils.delete_all_users()
        await self.redis.close()
        await self.redis.connection_pool.disconnect() # type: ignore
        await Tortoise.close_connections()

    async def test_1_get_all_languages(self):

        """test the get all language endpoint"""

        response = test_user_1.get_all_languages()
        self.assertEqual(response.status_code, requests.codes.ok)
        
        # check the format
        try:
            parsed_response = LanList(**response.json()['data'])
        except ValidationError:
            self.fail(f'The format of the language list is incorrect {response.json()["data"]}')

    async def test_2_add_language(self):

        """test the add language endpoint"""

        # not logged in -> unauthorized
        response = test_user_1.add_language(name='cpp')
        self.assertEqual(response.status_code, requests.codes.unauthorized)

        # not an admin -> forbidden
        test_user_1.login()
        response = test_user_1.add_language(name='cpp')
        self.assertEqual(response.status_code, requests.codes.forbidden)

        # incorrect format -> bad request
        default_admin.login()
        response = default_admin.add_language(name='cpp')
        self.assertEqual(response.status_code, requests.codes.bad_request)

        # language already exists -> conflict
        response = default_admin.add_language(
            name='cpp',
            file_ext='cpp',
            compile_cmd='g++ {src} -o {exe}',
            run_cmd='{exe}',
            image_name='gcc:14.3.0',
        )
        self.assertEqual(response.status_code, requests.codes.conflict)

        # correct format of a new language -> success
        response = default_admin.add_language(
            name='go',
            file_ext='go',
            compile_cmd='go build -o {exe} {src}',
            run_cmd='{exe}',
            image_name='golang:1.23',
        )
        self.assertEqual(response.status_code, requests.codes.ok)

        # use the language list to see whether the new language is in the system
        response = default_admin.get_all_languages()
        lan_list = response.json()['data']['name']
        if 'go' not in lan_list:
            self.fail('The new language is not in the language list')

        test_user_1.logout()
        default_admin.logout()

if __name__ == "__main__":
    unittest.main()
