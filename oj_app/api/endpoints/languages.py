from fastapi import status, APIRouter, Response, Request
from pydantic import ValidationError
from oj_app.models.schemas import Language
from oj_app.dependencies import common
import os
import json
import aiofiles

router = APIRouter(prefix='/languages')

LANGUAGES_DIR = os.path.join(os.curdir, "languages")

@router.post('/')
async def sign_up_language(language_data: dict, request: Request, response: Response):

    """sign up a new language"""

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
    
    # store the language
    file_name = f"{new_language.name}.json"
    async with aiofiles.open(os.path.join(LANGUAGES_DIR, file_name), 'w', encoding='utf-8') as f:
        await f.write(json.dumps(new_language))

    return {
        'code': status.HTTP_200_OK,
        'msg': 'success',
        'data': {'name': new_language.name},
    }

@router.get('/')
async def get_languages():

    """gets all available languages in the system"""

    languages = [file[:len(file) - len('.json')] for file in LANGUAGES_DIR]
    return {
        'code': status.HTTP_200_OK,
        'msg': 'success',
        'data': {'name': languages},
    }
