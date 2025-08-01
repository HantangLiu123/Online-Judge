from fastapi import APIRouter, Request, Response, status, BackgroundTasks
from oj_app.dependencies import common
from oj_app.core.security.UserManager import userManager
from oj_app.core.submission.ResolveManager import resolveManager
from oj_app.core.submission.SubmissionResManager import submissionResultManager
from oj_app.core.submission.TestLogManager import testLogManager
from oj_app.core.config import logs
import os
import asyncio
import aiofiles
import json

router = APIRouter(prefix='/export')

LAN_DIR = os.path.join(os.curdir, 'languages')
PROB_DIR = os.path.join(os.curdir, 'problems')

async def get_json(path: str):

    """gets the data in the json file according to the path"""

    async with aiofiles.open(path, 'r', encoding='utf-8') as f:
        content = await f.read()
    data = json.loads(content)
    return data

@router.get('/')
async def export_data(
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
):
    
    """export all data"""

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
    
    # export the data
    data = {}

    # get data from the database
    data['users'] = await userManager.export_users()
    submissions = await submissionResultManager.export_submissions()
    for submission in submissions:
        sub_id = submission['id']
        submission['details'] = await testLogManager.get_logs(sub_id)
    data['submissions'] = submissions
    data['resolves'] = await resolveManager.export_resolve_relation()

    # get problems and languages
    prob_names = os.listdir(PROB_DIR)
    prob_tasks = [get_json(os.path.join(PROB_DIR, name)) for name in prob_names]
    data['problems'] = await asyncio.gather(*prob_tasks)
    lan_names = os.listdir(LAN_DIR)
    lan_tasks = [get_json(os.path.join(LAN_DIR, name)) for name in lan_names]
    data['languages'] = await asyncio.gather(*lan_tasks)

    # record who export the data
    message = f"admin {current_user['username']} (id: {current_user['user_id']}) exports the data"
    background_tasks.add_task(logs.write_data_log, message)
    return {
        'code': status.HTTP_200_OK,
        'msg': 'success',
        'data': data,
    }
