from fastapi import status, APIRouter, Depends, HTTPException
from fastapi_cache import FastAPICache
from redis.asyncio import Redis as AioRedis
from api.core.security import auth
from shared.schemas import LanguageSchema
from shared.models import User
from shared.db import language_db

router = APIRouter(prefix='/langauges')

@router.post('/')
async def add_new_language(
    language: LanguageSchema,
    current_user: User = Depends(auth.get_current_user_factory(True)),
):
    
    """add a new language to the system"""

    # get the redis client
    redis: AioRedis = FastAPICache.get_backend().redis # type: ignore
    if await language_db.create_language_in_db(language, redis):
        return {
            'code': status.HTTP_200_OK,
            'msg': 'langauge registered',
            'data': {'name': language.name},
        }
    
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            'code': status.HTTP_409_CONFLICT,
            'msg': 'the language already exists',
            'data': None,
        }
    )

@router.get('/')
async def get_all_languages():

    """get the language list"""

    # get the redis client
    redis: AioRedis = FastAPICache.get_backend().redis # type: ignore
    lan_list = await language_db.get_all_languages(redis)
    name_list = [lan.name for lan in lan_list]
    return {
        'code': status.HTTP_200_OK,
        'msg': 'success',
        'data': {'name': name_list},
    }
