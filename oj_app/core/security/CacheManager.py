from fastapi_cache import FastAPICache
from fastapi_cache.types import KeyBuilder
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable, Any, Optional, Tuple, Dict, Awaitable
from redis import asyncio as aioredis
from dataclasses import dataclass
from oj_app.dependencies import common
import hashlib
import math
import asyncio

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

    assert request is not None # for this key builder, there should always be a request
    # getting important information
    current_user = common.get_current_user(request)
    page: int = kwargs['page']
    page_size: int = kwargs['page_size']
    prefix = FastAPICache.get_prefix()

    # create the key
    user_info = hashlib.md5(
        f'{current_user["user_id"]}:{current_user["role"]}'.encode()
    ).hexdigest()
    return f'{prefix}:user_list:{page}:{page_size}:{user_info}'

async def user_list_deleter(user_id: int) -> None:

    """delete the user list cache by id (an integer > 0)"""

    # the only possible page sizes are listed bellow
    possible_page_size = [10, 20, 50, 100]
    for page_size in possible_page_size:
        page = math.ceil(user_id / page_size)
        namespace = f'user_list:{page}:{page_size}'
        await FastAPICache.clear(namespace)

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

    assert request is not None # the request cannot be none in this condition
    # getting information
    current_user = common.get_current_user(request)
    user_id_filter: Optional[int] = kwargs.get('user_id')
    problem_id_filter: Optional[str] = kwargs.get('problem_id')
    status_filter: Optional[str] = kwargs.get('submission_status')
    page: int = kwargs['page']
    page_size: int = kwargs['page_size']
    prefix = FastAPICache.get_prefix()

    # create the key
    user_info = hashlib.md5(
        f'{current_user["user_id"]}:{current_user["role"]}'.encode()
    ).hexdigest()
    return f'{prefix}:submission_list:{user_id_filter}:{problem_id_filter}:{status_filter}:{page}:{page_size}:{user_info}'

async def submission_list_deleter(
    submission_id: str | None = None,
    user_id: int | None = None,
    problem_id: str | None = None,
) -> None:

    """delete submission list cache by id or filters"""

    # four parameters cannot all be none
    if submission_id is None and user_id is None and problem_id is None:
        raise ValueError('four parameters cannot all be none')
    
    if submission_id is not None:
        # delete by id
        redis: aioredis.Redis = FastAPICache.get_backend().redis # type: ignore

        # get the submission keys
        prefix = FastAPICache.get_prefix()
        submission_key_pattern = f'{prefix}:submission:{submission_id}:*'
        cursor = 0
        submission_keys: list[bytes] = []
        while True:
            cursor, keys = await redis.scan(
                cursor=cursor,
                match=submission_key_pattern,
                count=1000,
            )
            submission_keys.extend(keys)
            if cursor == 0:
                break

        # get all submission cache patterns
        cache_pattern_tasks = [redis.get(key.decode()) for key in submission_keys]
        submission_cache_patterns: list[bytes] = await asyncio.gather(*cache_pattern_tasks)

        # delete related cache
        delete_tasks = [FastAPICache.clear(namespace=pattern.decode()) for pattern in submission_cache_patterns]
        await asyncio.gather(*delete_tasks)
    else:
        # delete by filter
        patterns = []
        if user_id is not None:
            patterns.append(f'submission_list:{user_id}')
        if problem_id is not None:
            patterns.append(f'submission_list:*:{problem_id}')

        for pattern in patterns:
            await FastAPICache.clear(namespace=pattern)

@dataclass
class TaskFuncs:
    key_builder: KeyBuilder
    deleter: Callable[..., Awaitable[Any]]

class CacheManager:

    """this class manages the cache of the system"""

    def __init__(self) -> None:
        self.task_funcs_map: dict[str, TaskFuncs] = {}

    def init_tasks(self) -> None:
        
        """init the tasks"""

        self.add_task('user_list', user_list_key_builder, user_list_deleter)
        self.add_task('submission_list', submission_list_key_builder, submission_list_deleter)
    
    def add_task(
        self,
        task: str,
        key_builder: KeyBuilder,
        deleter: Callable[..., Awaitable[Any]],
    ) -> None:

        """add a task and its correponding functions"""

        self.task_funcs_map[task] = TaskFuncs(key_builder, deleter)

    @classmethod
    async def store_id_key_map(
        cls,
        id: Any,
        item_type: str,
        cache_type: str,
        expire: int,
        **kwargs,
    ) -> None:
        
        """stores the mapping of an id and its cache key"""

        backend = FastAPICache.get_backend()
        prefix = FastAPICache.get_prefix()
        key_strs = [prefix, item_type, str(id)]
        value_strs = [cache_type]
        for _, data in kwargs.items():
            key_strs.append(str(data))
            value_strs.append(str(data))
        value_strs.append('*')
        key = ':'.join(key_strs)
        value = ':'.join(value_strs).encode()
        await backend.set(key, value, expire)

cacheManager = CacheManager()
cacheManager.init_tasks()
