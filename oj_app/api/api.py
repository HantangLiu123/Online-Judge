from fastapi import APIRouter
from .endpoints import problems_manager, authorization, users, languages, submissions
from .endpoints import reset, export_data

# set the prefix for api, and add all routers
router = APIRouter(prefix='/api')
router.include_router(problems_manager.router)
router.include_router(authorization.router)
router.include_router(users.router)
router.include_router(languages.router)
router.include_router(submissions.router)
router.include_router(reset.router)
router.include_router(export_data.router)
