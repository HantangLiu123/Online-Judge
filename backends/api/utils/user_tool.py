import asyncio
import bcrypt
from typing import Literal
from fastapi.concurrency import run_in_threadpool
from . import shared_tool
from shared.models import User
from shared.schemas import UserCredentials, UserToCreate
from shared.utils import oj_cache
from shared.db import user_db

async def convert_user_info(
    user_credentials: UserCredentials,
    role: Literal['user', 'admin', 'banned'],
) -> UserToCreate:

    """this function converts the user sign in info to the info needed for db"""

    hashed_password = await run_in_threadpool(
        bcrypt.hashpw,
        user_credentials.password.encode(),
        bcrypt.gensalt(),
    )

    return UserToCreate(
        username=user_credentials.username,
        hashed_password=hashed_password.decode(),
        role=role,
    )

async def user_list_paginated(current_user: User, page: int, page_size: int) -> tuple[int, int, list[dict]]:

    """get the total number of users, the max page, and the corresponding page"""

    total, total_pages, users = await shared_tool.get_list_paginated(
        type=User,
        page=page,
        page_size=page_size,
        needed_info=['id', 'username', 'role', 'join_time', 'submit_count', 'resolve_count'],
    )

    # store the cache map
    map_tasks = [oj_cache.store_info_key_map(
        item_type='user',
        cache_key=oj_cache.user_list_key(current_user, page, page_size),
        expire=120,
        user_id=user['id'],
    ) for user in users]
    await asyncio.gather(*map_tasks)

    return total, total_pages, users

async def create_default_admin():

    """create the default admin"""

    admin = await convert_user_info(
        UserCredentials(
            username='admin',
            password='admin',
        ),
        'admin',
    )
    admin_id = await user_db.create_user_in_db(admin)
    if admin_id is None:
        print('the default admin is already created')
