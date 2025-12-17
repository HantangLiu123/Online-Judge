from datetime import datetime
from typing import Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from arq import ArqRedis
from api.core.security import auth
from api.utils import submission_tool
from shared.models import User, SubmissionStatus, UserRole
from shared.schemas import SubmissionPostModel
from shared.db import problem_db, language_db, submission_db
from shared.utils import oj_cache
import uuid

router = APIRouter(prefix='/submissions')
logger = logging.getLogger('debug')

@router.post('/')
async def submit_code(
    submission: SubmissionPostModel,
    current_user: User = Depends(auth.get_current_user_protected),
):
    
    """submit the code of a problem with the corresponding language"""

    logger.debug('inside submit code')
    problem = await problem_db.get_problem_by_id(submission.problem_id)
    if problem is None:
        # the problem does not exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'code': status.HTTP_404_NOT_FOUND,
                'msg': 'the problem does not exist',
                'data': None,
            }
        )
    logger.debug('problem got')
    
    redis: ArqRedis = FastAPICache.get_backend().redis # type: ignore
    lan_config = await language_db.get_language(submission.language, redis)
    if lan_config is None:
        # the language is not supported
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'code': status.HTTP_404_NOT_FOUND,
                'msg': 'the language is not supported',
                'data': None,
            }
        )
    logger.debug('language got')
    
    if not await submission_tool.allow_to_submit(redis, current_user.id):
        # the user exceeds the submission limit
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                'code': status.HTTP_429_TOO_MANY_REQUESTS,
                'msg': 'the user submits too many times',
                'data': None,
            }
        )
    
    logger.debug('begin to create submission')
    # create the submission
    created = False
    submission_time = datetime.now()
    submission_id = None
    while not created:
        submission_id = str(uuid.uuid4())
        logger.debug(f'submission_id generated: {submission_id}')
        created = await submission_db.create_submission_in_db(
            submission=submission,
            submission_id=submission_id,
            user_id=current_user.id,
            submission_time=submission_time,
            status=SubmissionStatus.PENDING,
        )
    await submission_tool.record_submission(redis, current_user.id, submission_time)
    await redis.enqueue_job('judge_task', submission_id)
    return {
        'code': status.HTTP_200_OK,
        'msg': 'success',
        'data': {'submission_id': submission_id, 'status': 'pending'},
    }

@router.get('/{submission_id}')
async def get_submission(
    submission_id: str,
    current_user: User = Depends(auth.get_current_user_protected),
):

    """get the submission by id"""

    submission = await submission_db.get_submission_in_db(submission_id)
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'code': status.HTTP_404_NOT_FOUND,
                'msg': 'the submission does not exist',
                'data': None,
            }
        )
    
    logger.debug(f"submission's user id is {submission.user_id}") #type: ignore
    if submission.user_id != current_user.id and current_user.role != UserRole.ADMIN: #type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                'code': status.HTTP_403_FORBIDDEN,
                'msg': 'the user is forbiddened to see this submission',
                'data': None,
            }
        )
    
    return {
        'code': status.HTTP_200_OK,
        'msg': 'success',
        'data': {
            'score': submission.score,
            'counts': submission.counts,
        }
    }

@router.get('/')
@cache(
    expire=120,
    key_builder=oj_cache.submission_list_key_builder,
)
async def get_submission_list(
    user_id: Optional[int] = Query(None),
    problem_id: Optional[str] = Query(None),
    submission_status: Optional[SubmissionStatus] = Query(None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    current_user: User = Depends(auth.get_current_user_protected),
):
    
    """return the submission list according to the params"""

    # parameters check
    logger.debug(f"user_id: {user_id}, problem_id: {problem_id}")
    if user_id is None and problem_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                'code': status.HTTP_400_BAD_REQUEST,
                'msg': 'user id and submission id cannot be empty at the same time',
                'data': None,
            }
        )
    if user_id is None and current_user.role != UserRole.ADMIN:
        user_id = current_user.id
    filters = {'user_id': user_id, 'problem_id': problem_id, 'status': submission_status}
    filters = {k: v for k, v in filters.items() if v is not None}
    total, total_page, submissions = await submission_tool.submission_list_paginated(
        page=page,
        page_size=page_size,
        current_user=current_user,
        **filters,
    )
    return {
        'statis': status.HTTP_200_OK,
        'message': 'success',
        'data': {
            'total': total,
            'total_page': total_page,
            'submissions': submissions,
        },
    }

@router.put('/{submission_id}/rejudge')
async def rejudge_code(submission_id: str, current_user: User = Depends(auth.get_current_user_admin_only)):

    """rejudge the submission with the submission id"""

    submission = await submission_db.get_submission_in_db(submission_id)
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'code': status.HTTP_404_NOT_FOUND,
                'msg': 'the submission does not exist',
                'data': None,
            }
        )
    await submission_db.update_submission_in_db(submission, SubmissionStatus.PENDING)
    redis: ArqRedis = FastAPICache.get_backend().redis # type: ignore
    await redis.enqueue_job('judge_task', submission_id)
    return {
        'code': status.HTTP_200_OK,
        'msg': 'rejudge started',
        'data': {'submission_id': submission_id, 'status': 'pending'}
    }

@router.get('/{submission_id}/log')
async def get_submission_log(
    submission_id: str,
    current_user: User = Depends(auth.get_current_user_protected),
):
    
    """get the detailed submission log"""

    submission, tests = await submission_db.get_submission_log_in_db(submission_id)
    # check for errors and authority
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'code': status.HTTP_404_NOT_FOUND,
                'msg': 'the submission does not exist',
                'data': None,
            }
        )
    if submission.user_id != current_user.id and current_user.role != UserRole.ADMIN: #type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                'code': status.HTTP_403_FORBIDDEN,
                'msg': 'the user is forbiddened to see this submission',
                'data': None,
            }
        )
    
    return {
        'code': status.HTTP_200_OK,
        'msg': 'success',
        'data': {
            'details': tests,
            'score': submission.score,
            'counts': submission.counts,
        }
    }
