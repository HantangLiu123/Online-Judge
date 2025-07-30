from fastapi import status, Request, Response, APIRouter, Query
from pydantic import ValidationError
from typing import Optional
from oj_app.dependencies import common
from oj_app.models.schemas import SubmissionPostModel
from oj_app.core.submission.SubmissionResManager import submissionResultManager
from oj_app.core.submission.TestLogManager import testLogManager
from oj_app.core.security.UserManager import userManager
import asyncio
import os

router = APIRouter(prefix='/submissions')

@router.post('/')
async def submit_code(
    request: Request,
    response: Response,
    submission_data: dict,
):
    
    """user can submit code through this"""

    PROBLEMS_PATH = os.path.join(os.curdir, "problems")

    try:
        current_user = common.get_current_user(request)
    except common.AuthenticationError:
        # the user has not logged in
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'code': status.HTTP_401_UNAUTHORIZED,
            'msg': 'the user has not logged in',
            'data': None,
        }
    
    try:
        submission = SubmissionPostModel(**submission_data)
    except ValidationError:
        # the format of the data is not correct
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'code': status.HTTP_400_BAD_REQUEST,
            'msg': 'the format of the submission is not correct',
            'data': None,
        }
    
    if not await request.app.state.judge_queue.allow_to_submit(
        user_id=current_user['user_id']
    ):
        # the user's frequency of submitting is too large
        response.status_code = status.HTTP_429_TOO_MANY_REQUESTS
        return {
            'code': status.HTTP_429_TOO_MANY_REQUESTS,
            'msg': 'user sends too many submissions',
            'data': None,
        }
    
    problem_ids = [file_name[:len(file_name) - len('.json')] for file_name in os.listdir(PROBLEMS_PATH)]
    if submission.problem_id not in problem_ids:
        # cannot find the problem
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'code': status.HTTP_404_NOT_FOUND,
            'msg': 'no such problem',
            'data': None,
        }
    
    if submission.language not in request.app.state.languages:
        # cannot find the language
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'code': status.HTTP_404_NOT_FOUND,
            'msg': 'the language is not supported',
            'data': None,
        }
    
    # move the submission into the queue
    submission_id = await request.app.state.judge_queue.enqueue_judge_task(
        judge_data=submission,
        user_id=current_user['user_id'],
    )
    # add submit counts
    await userManager.add_submit_count(current_user['user_id'])
    return {
        'code': status.HTTP_200_OK,
        'msg': 'success',
        'data': {
            'submission_id': submission_id,
            'status': 'pending',
        }
    }

@router.get('/{submission_id}')
async def get_submission(request: Request, response: Response, submission_id: str):

    """get the submission info by the id"""

    try:
        current_user = common.get_current_user(request)
    except common.AuthenticationError:
        # the user has not logged in
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'code': status.HTTP_401_UNAUTHORIZED,
            'msg': 'the user has not logged in',
            'data': None,
        }
    
    submission = await submissionResultManager.get_submission_by_id(submission_id)
    if not submission:
        # the submission does not exist
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'code': status.HTTP_404_NOT_FOUND,
            'msg': 'the submission does not exist',
            'data': None,
        }
    
    if current_user['user_id'] != submission['user_id'] and \
    current_user['role'] != 'admin':
        # the user's authority is not enough
        response.status_code = status.HTTP_403_FORBIDDEN
        return {
            'code': status.HTTP_403_FORBIDDEN,
            'msg': "the user's authority is not enough",
            'data': None,
        }
    
    if submission['status'] == 'success':
        return {
            'code': status.HTTP_200_OK,
            'msg': 'success',
            'status': submission['status'],
            'score': submission['score'],
            'counts': submission['counts'],
        }
    else:
        return {
            'code': status.HTTP_200_OK,
            'msg': 'success',
            'status': submission['status']
        }
    
@router.get('/')
async def get_submission_list(
    request: Request,
    response: Response,
    user_id: Optional[int] = Query(default=None),
    problem_id: Optional[str] = Query(default=None),
    submission_status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
):
    
    """return the submission list according to the parameters"""

    try:
        current_user = common.get_current_user(request)
    except common.AuthenticationError:
        # the user has not logged in
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'code': status.HTTP_401_UNAUTHORIZED,
            'msg': 'the user has not logged in',
            'data': None,
        }
    
    if current_user['role'] != 'admin' and (user_id is None \
    or user_id != current_user['user_id']):
        # the user's authority is not enough
        response.status_code = status.HTTP_403_FORBIDDEN
        return {
            'code': status.HTTP_403_FORBIDDEN,
            'msg': "the user's authority is not enough",
            'data': None,
        }
    
    # get the submission list
    total, submissions = await submissionResultManager.get_submission_list(
        user_id=user_id,
        problem_id=problem_id,
        status=submission_status,
        page=page,
        page_size=page_size,
    )

    return {
        'code': status.HTTP_200_OK,
        'msg': 'success',
        'data': {
            'total': total,
            'submissions': submissions,
        },
    }

@router.put('/{submission_id}/rejudge')
async def rejudge_submission(
    request: Request,
    response: Response,
    submission_id: str,
):
    
    """rejudge the submission according to the submission id"""

    try:
        current_user = common.get_current_user(request)
    except common.AuthenticationError:
        # the user has not logged in
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'code': status.HTTP_401_UNAUTHORIZED,
            'msg': 'the user has not logged in',
            'data': None,
        }
    
    if current_user['role'] != 'admin':
        # the user's authority is not enough
        response.status_code = status.HTTP_403_FORBIDDEN
        return {
            'code': status.HTTP_403_FORBIDDEN,
            'msg': "the user's authority is not enough",
            'data': None,
        }
    
    try:
        # put the task into the queue
        await request.app.state.judge_queue.enqueue_rejudge(submission_id)
    except ValueError:
        # cannot find the original submission
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'code': status.HTTP_404_NOT_FOUND,
            'msg': 'no such submission',
            'data': None,
        }
    
    return {
        'code': status.HTTP_200_OK,
        'msg': 'rejudge started',
        'data': {
            'submission_id': submission_id,
            'status': 'pending',
        },
    }

@router.get('/{submission_id}/log')
async def get_submission_log(
    request: Request,
    response: Response,
    submission_id: str,
):
    
    """get the detailed log of the submission"""

    try:
        current_user = common.get_current_user(request)
    except common.AuthenticationError:
        # the user has not logged in
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'code': status.HTTP_401_UNAUTHORIZED,
            'msg': 'the user has not logged in',
            'data': None,
        }
    
    submission = await submissionResultManager.get_submission_by_id(submission_id)
    if not submission:
        # the submission does not exist
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'code': status.HTTP_404_NOT_FOUND,
            'msg': 'the submission does not exist',
            'data': None,
        }
    
    if current_user['user_id'] != submission['user_id'] and \
    current_user['role'] != 'admin':
        # the user's authority is not enough
        response.status_code = status.HTTP_403_FORBIDDEN
        return {
            'code': status.HTTP_403_FORBIDDEN,
            'msg': "the user's authority is not enough",
            'data': None,
        }
    
    test_logs = await testLogManager.get_logs(submission_id)
    return {
        'code': status.HTTP_200_OK,
        'msg': 'success',
        'data': {
            'submission': submission,
            'details': test_logs,
        },
    }
