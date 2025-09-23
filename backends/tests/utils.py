import asyncio
from typing import Literal
from shared.models import User, UserRole
from shared.schemas import UserCredentials
from api.utils import user_tool

async def test_init():

    """adding 200 users for tests"""

    user_credentials = [
        UserCredentials(
            username=f'test_user_{i}',
            password=f'test_user_{i}',
        ) for i in range(1, 201)
    ]
    convert_tasks = [user_tool.convert_user_info(credential, 'user') for credential in user_credentials]
    users = await asyncio.gather(*convert_tasks)
    for user in users:
        # use the for loop to ensure the id and the username and passwords are corresponding
        await User.create(
            username=user.username,
            password=user.hashed_password,
            role=user.role,
        )

async def delete_all_users():

    """delete all users except for the default admin"""

    await User.filter(username__not='admin').delete()

async def user_factory(user_credential: UserCredentials, role: Literal['user', 'admin', 'banned']):

    """create a user"""

    user_to_create = await user_tool.convert_user_info(user_credential, role)
    await User.create(
        username=user_to_create.username,
        password=user_to_create.hashed_password,
        role=user_to_create.role,
    )

async def user_destroy(username: str):

    """delete a user"""

    user = await User.get(username=username)
    await user.delete()

async def change_user_role(username: str, role: str):

    """change the role of a user"""

    user = await User.get(username=username)
    user.role = UserRole(role)
    await user.save()
