import hashlib
import asyncio
import uuid
from fastapi_cache import FastAPICache
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable, Any, Optional, Tuple, Dict
from arq.connections import ArqRedis
from ..models import User

async def store_info_key_map(
    item_type: str,
    cache_key: str,
    expire: int,
    **kwargs,
): 
    
    """stores the mapping of info (id/filter and its cache key)"""

    backend = FastAPICache.get_backend()
    prefix = FastAPICache.get_prefix()

    # build the key for each item and store
    items_keys = [
        hashlib.md5(f'{item_type}:{item[0]}:{item[1]}'.encode()).hexdigest() for item in kwargs.items()
    ]
    map_to_store = [
        backend.set(f'{prefix}:{key}:{uuid.uuid4()}', cache_key.encode(), expire) for key in items_keys
    ] # using uuid to minimize the possibility of duplicating item_keys due to multiple checks
    await asyncio.gather(*map_to_store)

async def _delete_cache_by_pattern(key_pattern: str):

    """find and delete the cache according to the key pattern"""

    prefix = FastAPICache.get_prefix()
    redis: ArqRedis = FastAPICache.get_backend().redis # type: ignore
    cursor = 0
    keys_to_delete: list[bytes] = []

    # scan to find the keys to delete
    while True:
        cursor, keys = await redis.scan(
            cursor=cursor,
            match=f'{prefix}:{key_pattern}:*',
            count=1000,
        )
        keys_to_delete.extend(keys)
        # delete the keys that has been scanned
        await redis.delete(*keys)
        if cursor == 0:
            break

    # delete cache according to the keys
    decoded_keys = [key.decode() for key in keys_to_delete]
    await redis.delete(*decoded_keys)

async def delete_cache(
    item_type: str,
    **kwargs,
):
    
    """delete the corresponding cache"""

    key_patterns = [
        hashlib.md5(f'{item_type}:{item[0]}:{item[1]}'.encode()).hexdigest() for item in kwargs.items()
    ]
    delete_tasks = [_delete_cache_by_pattern(pattern) for pattern in key_patterns]
    await asyncio.gather(*delete_tasks)

def user_list_key(
    current_user: User,
    page: int,
    page_size: int,
) -> str:
    
    """build the key for a user list cache"""

    prefix = FastAPICache.get_prefix()
    cache_key = hashlib.md5(
        f'user_list:{page}:{page_size}:{current_user.id}:{current_user.role}'.encode()
    ).hexdigest()
    return f'{prefix}:{cache_key}'

def user_list_key_builder(
    func: Callable[..., Any],
    namespace: str = "",
    *,
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
) -> str:
    
    """the key builder for user list cache"""

    # getting information from kwargs
    current_user: User = kwargs['current_user']
    page = kwargs['page']
    page_size = kwargs['page_size']

    # create the key
    return user_list_key(current_user, page, page_size)

def submission_list_key(
    current_user: User,
    user_id_filter: Optional[int],
    problem_id_filter: Optional[str],
    status_filter: Optional[str],
    page: int,
    page_size: int,
) -> str:
    
    """create the cache key for the submission list"""

    prefix = FastAPICache.get_prefix()
    cache_key = hashlib.md5(
        f'submission_list:{user_id_filter}:{problem_id_filter}:{status_filter}:{page}:{page_size}:{current_user.id}:{current_user.role}'.encode()
    ).hexdigest()
    return f'{prefix}:{cache_key}'

def submission_list_key_builder(
    func: Callable[..., Any],
    namespace: str = "",
    *,
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
) -> str:
    
    """the key builder for the submission list request"""

    # get information from kwargs
    current_user: User = kwargs['current_user']
    user_id_filter: Optional[int] = kwargs.get('user_id')
    problem_id_filter: Optional[str] = kwargs.get('problem_id')
    status_filter: Optional[str] = kwargs.get('submission_status')
    page: int = kwargs['page']
    page_size: int = kwargs['page_size']

    # create the key
    return submission_list_key(
        current_user,
        user_id_filter,
        problem_id_filter,
        status_filter,
        page,
        page_size,
    )

def problem_list_key(
    page: int,
    page_size: int,
    hardness: Optional[str],
) -> str:
    
    """create the cache key for the problem list"""

    prefix = FastAPICache.get_prefix()
    cache_key = hashlib.md5(
        f'problem_list:{page}:{page_size}:{hardness}'.encode()
    ).hexdigest()
    return cache_key

def problem_list_key_builder(
    func: Callable[..., Any],
    namespace: str = "",
    *,
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
):
    
    """the cache key builder for the problem list"""

    # getting information
    page = kwargs['page']
    page_size = kwargs['page_size']
    hardness = kwargs.get('hardness')

    # create the key
    return problem_list_key(page, page_size, hardness)

async def clear_cache():

    """clear all caches"""

    await FastAPICache.clear()
