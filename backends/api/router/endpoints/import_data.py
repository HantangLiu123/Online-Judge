import asyncio
from fastapi import APIRouter, Depends, status
from redis.asyncio import Redis as AioRedis
from api.core.security import auth
from shared.db import user_db, problem_db, language_db, submission_db, resolve_db
from shared.utils import user_parse, problem_parse, language_parse, submission_parse, resolve_parse
from shared.schemas import ImportData

router = APIRouter(prefix='/import')

@router.post('/')
async def import_data(
    data: ImportData,
    current_user = Depends(auth.get_current_user_admin_only),
):
    
    """import the data in the payload"""

    user_to_create = [user_parse.user_data_to_user(user) for user in data.users]
    await user_db.import_user_in_db(user_to_create)
    problem_to_create = [problem_parse.problem_schema_to_problem(problem) for problem in data.problems]
    await problem_db.import_problem_in_db(problem_to_create)
    language_to_create = [language_parse.language_schema_to_language(language) for language in data.languages]
    await language_db.import_language_in_db(language_to_create)
    redis: AioRedis = FastAPICache.get_backend().redis # type: ignore
    await language_db.init_lan_in_redis(redis)
    await submission_db.import_submission_to_db(data.submissions)
    resolve_to_create = [resolve_parse.resolve_data_to_resolve(resolve) for resolve in data.resolves]
    await resolve_db.import_resolve_in_db(resolve_to_create)

    return {
        'code': status.HTTP_200_OK,
        'msg': 'import success',
        'data': None,
    }
