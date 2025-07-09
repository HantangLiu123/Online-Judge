from fastapi import APIRouter
from .endpoints import problems_manager

# set the prefix for api, and add all routers
router = APIRouter(prefix='/api')
router.include_router(problems_manager.router)
