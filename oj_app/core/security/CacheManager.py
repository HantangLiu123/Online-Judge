from fastapi_cache import FastAPICache
from fastapi_cache.types import KeyBuilder
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable, Any, Optional, Tuple, Dict, Awaitable
from dataclasses import dataclass
from oj_app.dependencies import common
import hashlib
import math

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
    
    def add_task(
        self,
        task: str,
        key_builder: KeyBuilder,
        deleter: Callable[..., Awaitable[Any]],
    ) -> None:

        """add a task and its correponding functions"""

        self.task_funcs_map[task] = TaskFuncs(key_builder, deleter)

cacheManager = CacheManager()
cacheManager.init_tasks()
