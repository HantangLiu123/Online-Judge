from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi_cache.decorator import cache
from api.core.security import auth
from api.utils import problem_tool
from shared.models import User, UserRole
from shared.schemas import ProblemSchema
from shared.utils import oj_cache
from shared.db import problem_db

router = APIRouter(prefix='/problems')

@router.get('/')
@cache(expire=120, key_builder=oj_cache.problem_list_key_builder)
async def get_problems_list(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    hardness: Literal['easy', 'medium', 'hard'] | None = Query(...),
):
    
    """returns the problem list according to the page, page size, and hardness"""

    total, total_page, problems = await problem_tool.problem_list_paginated(
        page=page,
        page_size=page_size,
        hardness=hardness,
    )
    return {
        'code': status.HTTP_200_OK,
        'msg': 'success',
        'data': {
            'total': total,
            'total_page': total_page,
            'problems': problems,
        }
    }

@router.post('/')
async def create_problem(
    problem: ProblemSchema,
    current_user: User = Depends(auth.get_current_user_factory(False)),
):
    
    """the endpoint for uploading a problem"""

    if not await problem_db.create_problem_in_db(problem):
        # the id is repeated
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                'code': status.HTTP_409_CONFLICT,
                'msg': 'problem id conflict',
                'data': None,
            }
        )
    
    return {
        'code': status.HTTP_200_OK,
        'msg': 'success',
        'data': {'id': problem.id},
    }

@router.get('/{problem_id}')
async def get_problem(
    problem_id: str,
    current_user: User | None = Depends(auth.get_current_user_login)   # use this since getting a problem does not require to be logged in
):

    """get a problem by its id
    
    This endpoint returns the info of the problem according to the id.
    Users who are not admins can only see the samples but not testcases.
    """

    problem = await problem_db.get_problem_by_id(problem_id)
    if not problem:
        # the problem does not exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'code': status.HTTP_404_NOT_FOUND,
                'msg': 'the problem does not exist',
                'data': None,
            }
        )
    
    if not current_user or current_user.role != UserRole.ADMIN:
        return {
            'code': status.HTTP_200_OK,
            'msg': 'success',
            'data': problem_tool.dump_testcases(problem),
        }
    else:
        return {
            'code': status.HTTP_200_OK,
            'msg': 'success',
            'data': problem,
        }
    
@router.delete('/{problem_id}')
async def delete_problem(
    problem_id: str,
    current_user: User = Depends(auth.get_current_user_factory(True)),
):
    
    """delete a problem according to the problem id"""

    problem = await problem_db.get_problem_by_id(problem_id)
    if not problem:
        # the problem does not exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'code': status.HTTP_404_NOT_FOUND,
                'msg': 'the problem does not exist',
                'data': None,
            }
        )
    
    # delete the problem
    await problem_db.delete_problem_in_db(problem)
    return {
        'code': status.HTTP_200_OK,
        'msg': 'delete success',
        'data': {'id': problem_id},
    }
