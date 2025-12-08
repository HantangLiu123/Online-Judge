import asyncio
from datetime import datetime, timedelta
from typing import Any
from redis.asyncio import Redis as aioredis
from . import shared_tool
from shared.models import Submission, User
from shared.utils import oj_cache

def within_a_minute(now: datetime, past: bytes | None) -> bool:

    """check if now is within a minute from past"""

    if past is None:
        return False
    return now - datetime.fromisoformat(past.decode()) < timedelta(minutes=1)

async def allow_to_submit(redis: aioredis, user_id: int) -> bool:

    """check if the user is allowed to submit or exceeds the submission limit of 3 per a minute"""

    now = datetime.now()
    while not within_a_minute(
        now=now,
        past=await redis.lindex(f'user_submission_timestamp:{user_id}', -1), # type: ignore
    ):
        await redis.rpop(f'user_submission_timestamp:{user_id}') # type: ignore
    return await redis.llen(f'user_submission_timestamp:{user_id}') < 3 # type: ignore

async def record_submission(redis: aioredis, user_id: int, submission_time: datetime):

    """record the submission of the user"""

    await redis.lpush(f'user_submission_timestamp:{user_id}', submission_time.isoformat()) #type: ignore

async def submission_list_paginated(
    page: int,
    page_size: int,
    current_user: User,
    **kwargs: dict[str, Any],
) -> tuple[int, int, list[dict]]:
    
    """return the submission list paginated"""

    # there must be something in the filter
    assert kwargs is not None
    total, total_page, submissions = await shared_tool.get_list_paginated(
        type=Submission,
        page=page,
        page_size=page_size,
        needed_info=['submission_id', 'status', 'score', 'counts'],
        order_term='submission_id',
        **kwargs,
    )
    
    # store the cache map
    map_tasks = [oj_cache.store_info_key_map(
        item_type='submission',
        cache_key=oj_cache.submission_list_key(
            current_user=current_user,
            user_id_filter=kwargs.get('user_id'), # pyright: ignore[reportArgumentType]
            problem_id_filter=kwargs.get('problem_id'), # pyright: ignore[reportArgumentType]
            status_filter=kwargs.get('status'), # pyright: ignore[reportArgumentType]
            page=page,
            page_size=page_size,
        ),
        expire=120,
        **kwargs,
    )]
    await asyncio.gather(*map_tasks)
    return total, total_page, submissions
