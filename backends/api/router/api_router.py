from fastapi import APIRouter
from .endpoints import (
    authorization,
    users,
    problems,
    languages,
    submissions,
    reset,
    export,
    import_data,
)

oj_router = APIRouter(prefix='/api')
oj_router.include_router(authorization.router)
oj_router.include_router(users.router)
oj_router.include_router(problems.router)
oj_router.include_router(languages.router)
oj_router.include_router(submissions.router)
oj_router.include_router(reset.router)
oj_router.include_router(export.router)
oj_router.include_router(import_data.router)
