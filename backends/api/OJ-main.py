from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from tortoise import Tortoise
from contextlib import asynccontextmanager
from arq import create_pool
from arq.connections import RedisSettings
from shared.settings import TORTOISE_ORM
from shared.db import language_db
from .core.config import settings
from .router.api_router import oj_router

# set the redis for the api and arq
redis_settings = RedisSettings(host=settings.redis_host)

@asynccontextmanager
async def lifespan(app: FastAPI):

    """initialize the api"""

    # init tortoise for database
    await Tortoise.init(config=TORTOISE_ORM)

    # init the arq and the redis
    redis = await create_pool(redis_settings)

    # init the cache
    FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')

    # init the languages
    await language_db.init_lan_in_redis(redis)

    # record the start up time of the api
    app.state.start_up_time = datetime.now()

    yield

    print('shutting down')

def create_app() -> FastAPI:

    """create the app"""

    app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
    app.include_router(oj_router)
    return app

app = create_app()

# add an exception handler for bad requests
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            'code': status.HTTP_400_BAD_REQUEST,
            'msg': 'the request format is incorrect',
            'data': None
        }
    )
