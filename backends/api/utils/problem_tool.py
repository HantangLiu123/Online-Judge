import asyncio
from typing import Literal
from . import shared_tool
from shared.models import Problem
from shared.utils import oj_cache, problem_parse

async def problem_list_paginated(
    page: int,
    page_size: int,
    hardness: Literal['easy', 'medium', 'hard'] | None = None,
) -> tuple[int, int, list[dict]]:
    
    """get the problem list paginated"""

    if hardness:
        # if there is hardness filter, tells the function
        total, total_page, problems = await shared_tool.get_list_paginated(
            type=Problem,
            page=page,
            page_size=page_size,
            needed_info=['id', 'title'],
            order_term='id',
            hardness=hardness,
        )
    else:
        # if not, 
        total, total_page, problems = await shared_tool.get_list_paginated(
            type=Problem,
            page=page,
            page_size=page_size,
            order_term='id',
            needed_info=['id', 'title'],
        )

    # store the cache map
    map_tasks = [oj_cache.store_info_key_map(
        item_type='problem',
        cache_key=oj_cache.problem_list_key(page, page_size, hardness),
        expire=120,
        problem_id=problem['id'],
    ) for problem in problems]
    await asyncio.gather(*map_tasks)

    return total, total_page, problems

def dump_testcases(problem: Problem) -> dict:

    """this function dumps the testcases in a problem away"""

    problem_info = problem_parse.problem_to_problem_schema(problem)
    problem_dict: dict = problem_info.model_dump()
    del problem_dict['testcases']
    return problem_dict
