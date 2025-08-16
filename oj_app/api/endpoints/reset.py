from fastapi import APIRouter, Request, Response, status, BackgroundTasks
from fastapi_cache import FastAPICache
from oj_app.dependencies import common
from oj_app.core.security.UserManager import userManager
from oj_app.core.submission.ResolveManager import resolveManager
from oj_app.core.submission.SubmissionResManager import submissionResultManager
from oj_app.core.submission.TestLogManager import testLogManager
from oj_app.core.config import logs
from oj_app.models.schemas import User
import os
import aiofiles.os
import asyncio

router = APIRouter(prefix='/reset')

PROBLEM_PATH = os.path.join(os.curdir, 'problems')
LANGUAGE_PATH = os.path.join(os.curdir, 'languages')

@router.post('/')
async def reset_data(
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
):

    """reset all data in the site"""

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
    
    # reset the database
    await userManager.delete_all_users()
    await resolveManager.delete_all_relation()
    await submissionResultManager.delete_all_submissions()
    await testLogManager.delete_all_logs()
    await request.app.state.judge_queue.flush_redis()

    # create the default admin
    await userManager.create_user(User(
        username='admin',
        password='admin',
        role='admin',
    ))

    # remove the logs
    logs.remove_all_log()

    # remove languages and problems
    rm_lan_tasks = [aiofiles.os.remove(os.path.join(LANGUAGE_PATH, file)) for file in os.listdir(LANGUAGE_PATH)]
    await asyncio.gather(*rm_lan_tasks)
    rm_prob_tasks = [aiofiles.os.remove(os.path.join(PROBLEM_PATH, file)) for file in os.listdir(PROBLEM_PATH)]
    await asyncio.gather(*rm_prob_tasks)

    # clear the cache
    await FastAPICache.clear()

    # record who reset the data
    message = f"admin {current_user['username']} (id: {current_user['user_id']}) reset all data"
    background_tasks.add_task(logs.write_data_log, message)

    return {
        'code': status.HTTP_200_OK,
        'msg': 'system reset successfully',
        'data': None,
    }
