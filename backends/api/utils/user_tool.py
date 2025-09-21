import asyncio
import bcrypt
from typing import Literal
from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool
from shared.models import User
from shared.schemas import UserCredentials, UserToCreate
from shared.utils import oj_cache

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

    total = await User.all().count()
    if total == 0:
        # returns a blank list
        return 0, 0, []
    
    total_pages = (total + page_size - 1) // page_size
    if page > total_pages:
        # the page does not exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'code': status.HTTP_404_NOT_FOUND,
                'msg': 'the page does not exist',
                'data': None,
            }
        )
    
    offset = (page - 1) * page_size
    users = await User.all().offset(offset).limit(page_size).values(
        'id', 'username', 'role', 'join_time', 'submit_count', 'resolve_count'
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

