from typing import Type
from tortoise import models
from fastapi import HTTPException, status

async def get_list_paginated(
    type: Type[models.Model],
    page: int,
    page_size: int,
    needed_info: list[str],
    order_term: str,
    **kwargs,
) -> tuple[int, int, list[dict]]:
    
    """get the paginated list according to the params"""

    # get the total number
    if kwargs:
        total = await type.filter(**kwargs).count()
    else:
        total = await type.all().count()

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
    if kwargs:
        return_list = await type.filter(**kwargs).offset(offset).limit(page_size).order_by(order_term).values(
            *needed_info
        )
    else:
        return_list = await type.all().offset(offset).limit(page_size).order_by(order_term).values(
            *needed_info
        )

    return total, total_pages, return_list
