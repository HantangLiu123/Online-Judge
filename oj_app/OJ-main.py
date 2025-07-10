from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from .core.config import settings
from .api.api import router as api_router

def create_app() -> FastAPI:

    """create the app according to settings, set up middlewares and router"""

    app = FastAPI(title=settings.app_name, dubug=settings.debug)
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
