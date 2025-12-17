from fastapi import APIRouter, Depends, status
from fastapi_cache import FastAPICache
from redis.asyncio import Redis as AioRedis
from api.core.security import auth
from shared.db import user_db, problem_db, language_db

router = APIRouter(prefix='/reset')

@router.post('/')
async def reset_data(current_user = Depends(auth.get_current_user_admin_only)):

    """reset the system"""

    redis: AioRedis = FastAPICache.get_backend().redis # type: ignore
    await user_db.reset_user_table()
    await problem_db.reset_problem_table()
    await language_db.reset_language_table(redis)
    await FastAPICache.clear()

    return {
        'code': status.HTTP_200_OK,
        'msg': 'system reset successfully',
        'data': None,
    }
