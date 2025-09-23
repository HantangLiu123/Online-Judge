from fastapi import APIRouter
from .endpoints import (
    authorization,
    users,
)

oj_router = APIRouter(prefix='/api')
oj_router.include_router(authorization.router)
oj_router.include_router(users.router)
