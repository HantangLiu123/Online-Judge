from fastapi import status, APIRouter, Response, Request, BackgroundTasks
from pydantic import ValidationError
from oj_app.models.schemas import Language
from oj_app.dependencies import common, language
from oj_app.core.config import logs
import os
import json
import aiofiles

router = APIRouter(prefix='/languages')

LANGUAGES_DIR = os.path.join(os.curdir, "languages")

@router.post('/')
async def sign_up_language(
    language_data: dict,
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
):

    """sign up a new language"""
    
    try:
        # get the user info
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
        # Forbidden since the user is not an admin
        response.status_code = status.HTTP_403_FORBIDDEN
        return {
            'code': status.HTTP_403_FORBIDDEN,
            'msg': 'the user does not have enough authority',
            'data': None,
        }
    
    try:
        # parse the language data into a Language model (pydantic)
        new_language = Language(**language_data)
    except ValidationError:
        # the parameters are incorrect
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'code': status.HTTP_400_BAD_REQUEST,
            'msg': 'the parameters are incorrect',
            'data': None,
        }
    
    # store the language and change the state
    file_name = f"{new_language.name}.json"
    lan_dict = new_language.model_dump()
    async with aiofiles.open(os.path.join(LANGUAGES_DIR, file_name), 'w', encoding='utf-8') as f:
        await f.write(json.dumps(lan_dict, indent=4, ensure_ascii=False))
    request.app.state.languages[new_language.name] = lan_dict

    # record in log
    message = f"admin {current_user['username']} (id: {current_user['user_id']}) create/change the configuration for the language {new_language.name}"
    background_tasks.add_task(logs.write_language_log, message)
    return {
        'code': status.HTTP_200_OK,
        'msg': 'success',
        'data': {'name': new_language.name},
    }

@router.get('/')
async def get_languages(request: Request):

    """gets all available languages in the system"""

    languages = list(request.app.state.languages.keys())
    return {
        'code': status.HTTP_200_OK,
        'msg': 'success',
        'data': {'name': languages},
    }
