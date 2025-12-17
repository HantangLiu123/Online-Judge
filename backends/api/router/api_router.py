from fastapi import APIRouter
from .endpoints import (
    authorization,
    users,
    problems,
    languages,
    submissions,
)

oj_router = APIRouter(prefix='/api')
oj_router.include_router(authorization.router)
oj_router.include_router(users.router)
oj_router.include_router(problems.router)
oj_router.include_router(languages.router)
oj_router.include_router(submissions.router)
