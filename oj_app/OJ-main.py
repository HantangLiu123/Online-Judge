from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from starlette.middleware.sessions import SessionMiddleware
from .core.config import settings
from .core.security.UserManager import userManager
from .api.api import router as api_router
from contextlib import asynccontextmanager
from .models.schemas import User

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    """initalize user system and cache system"""

    # user system init
    await userManager.create_user_table()
    admin = User(username='admin', password='admin', role='admin')
    try:
        await userManager.create_user(admin)
    except ValueError:
        print("Default admin already created")

    # cache system (redis)
    redis = aioredis.from_url('redis://localhost')
    FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')
    yield

    print('shutting down')

def create_app() -> FastAPI:

    """create the app according to settings, set up middlewares and router"""

    app = FastAPI(title=settings.app_name, dubug=settings.debug, lifespan=lifespan)
    app.add_middleware(
        SessionMiddleware, 
        secret_key = settings.secret_key, # type: ignore
        max_age = settings.session_max_age,
        same_site=settings.same_site, # type: ignore
        https_only=settings.session_https_only,
    )
    app.include_router(api_router)
    return app

app = create_app()
