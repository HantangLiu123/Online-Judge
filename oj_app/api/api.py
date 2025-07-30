from fastapi import APIRouter
from .endpoints import problems_manager, authorization, users, languages, submissions

# set the prefix for api, and add all routers
router = APIRouter(prefix='/api')
router.include_router(problems_manager.router)
router.include_router(authorization.router)
router.include_router(users.router)
router.include_router(languages.router)
router.include_router(submissions.router)
