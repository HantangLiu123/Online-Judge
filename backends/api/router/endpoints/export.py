import asyncio
from fastapi import APIRouter, Depends, status
from api.core.security import auth
from shared.db import user_db, problem_db, language_db, submission_db, resolve_db
from shared.utils import user_parse, problem_parse, language_parse, submission_parse, resolve_parse

router = APIRouter(prefix='/export')

@router.get('/')
async def export_data(current_user = Depends(auth.get_current_user_admin_only)):

    """export the data from the system"""

    users = await user_db.export_user_table()
    user_data = [user_parse.user_to_user_data(user) for user in users]
    problems = await problem_db.export_problem_table()
    problem_data = [problem_parse.problem_to_problem_schema(problem) for problem in problems]
    languages = await language_db.export_language_table()
    language_data = [language_parse.language_to_language_schema(language) for language in languages]
    submissions = await submission_db.export_submission_table()
    submission_parse_tasks = [submission_parse.parse_submission_to_data(submission) for submission in submissions]
    submission_data = await asyncio.gather(*submission_parse_tasks)
    resolves = await resolve_db.export_resolve_table()
    resolve_data = [resolve_parse.resolve_to_resolve_data(resolve) for resolve in resolves]

    return {
        'code': status.HTTP_200_OK,
        'msg': 'success',
        'data': {
            'users': user_data,
            'problems': problem_data,
            'languages': language_data,
            'submissions': submission_data,
            'resolves': resolve_data,
        }
    }
