from fastapi import APIRouter
from .endpoints import (
    authorization,
)

oj_router = APIRouter(prefix='/api')
oj_router.include_router(authorization.router)
