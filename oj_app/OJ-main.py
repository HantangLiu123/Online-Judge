from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from starlette.middleware.sessions import SessionMiddleware
from .core.config import settings
from .core.security.UserManager import userManager
from .core.submission.SubmissionResManager import submissionResultManager
from .core.submission.TestLogManager import testLogManager
from .core.submission.ResolveManager import resolveManager
from .core.judge.judge_queue import JudgeQueue
from .api.api import router as api_router
from contextlib import asynccontextmanager
from .models.schemas import User
from .dependencies import language

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    """initalize the api"""

    # user system init
    await userManager.create_user_table()
    admin = User(username='admin', password='admin', role='admin')
    try:
        await userManager.create_user(admin)
    except ValueError:
        print("Default admin already created")

    # submission system init
    await submissionResultManager.create_submission_table()
    await testLogManager.create_test_log_tables()
    await resolveManager.create_resolve_table()

    # cache system (redis)
    redis = aioredis.from_url(settings.redis_url)
    FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')

    # init the languages
    app.state.languages = await language.init_language()

    # judge queue
    judge_queue = JudgeQueue(redis, settings.max_workers)
    judge_queue.set_languages(app.state.languages)
    await judge_queue.start()
    app.state.judge_queue = judge_queue

    yield

    # shut down the queue and redis
    await judge_queue.stop()
    await redis.close()

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
