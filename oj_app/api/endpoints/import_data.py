from fastapi import APIRouter, Request, Response, status, BackgroundTasks
from fastapi_cache import FastAPICache
from pydantic import ValidationError
from oj_app.dependencies import common
from oj_app.models.schemas import ImportData, BaseModel
from oj_app.core.security.UserManager import userManager
from oj_app.core.submission.ResolveManager import resolveManager
from oj_app.core.submission.SubmissionResManager import submissionResultManager
from oj_app.core.submission.TestLogManager import testLogManager
from oj_app.core.config import logs
import os
import asyncio
import aiofiles
import json

router = APIRouter(prefix='/import')

LAN_DIR = os.path.join(os.curdir, 'languages')
PROB_DIR = os.path.join(os.curdir, 'problems')

async def import_model(path: str, model: BaseModel) -> None:

    """stores the model in the parameters at the path"""

    model_dict = model.model_dump()
    async with aiofiles.open(path, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(model_dict, indent=4, ensure_ascii=False))

@router.post('/')
async def import_data(
    request: Request,
    response: Response,
    data: dict,
    background_tasks: BackgroundTasks,
):
    
    """import data into the site"""

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
        data_imported = ImportData(**data)
    except ValidationError:
        # the data is not in the right format
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'code': status.HTTP_400_BAD_REQUEST,
            'msg': "the data's format is incorrect",
            'data': None,
        }
    
    # import data about the database
    await userManager.import_users(data_imported.users)
    await submissionResultManager.import_submissions(data_imported.submissions)
    await testLogManager.import_logs(data_imported.submissions)
    await resolveManager.import_resolve_relation(data_imported.resolves)

    # import the languages and problems
    lan_tasks = [import_model(os.path.join(LAN_DIR, f'{lan.name}.json'), lan) for lan in data_imported.languages]
    await asyncio.gather(*lan_tasks)
    prob_tasks = [import_model(os.path.join(PROB_DIR, f'{prob.id}.json'), prob) for prob in data_imported.problems]
    await asyncio.gather(*prob_tasks)

    # clear the cache
    await FastAPICache.clear()

    # record this import 
    message = f"admin {current_user['username']} (id: {current_user['user_id']}) import data to the site"
    background_tasks.add_task(logs.write_data_log, message)
    return {
        'code': status.HTTP_200_OK,
        'msg': 'import success',
        'data': None,
    }
