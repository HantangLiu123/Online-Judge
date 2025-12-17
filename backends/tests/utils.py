import asyncio
import os
import json
from typing import Literal
from redis.asyncio import Redis as AioRedis
from shared.models import User, UserRole, Problem, Language, Test
from shared.schemas import UserCredentials, ProblemSchema, LanguageSchema, SubmissionData
from shared.utils import problem_parse, language_parse, submission_parse
from api.utils import user_tool

async def test_init_large():

    """adding 200 users for tests"""

    user_credentials = [
        UserCredentials(
            username=f'test_user_{i}',
            password=f'test_user_{i}',
        ) for i in range(1, 201)
    ]
    convert_tasks = [user_tool.convert_user_info(credential, 'user') for credential in user_credentials]
    users = await asyncio.gather(*convert_tasks)
    user_to_create = [User(
        id=i + 2,
        username=user.username,
        password=user.hashed_password,
        role=user.role,
    ) for i, user in enumerate(users)]
    await User.bulk_create(user_to_create)

async def test_init_small():

    """adding 10 users for tests"""

    user_credentials = [
        UserCredentials(
            username=f'test_user_{i}',
            password=f'test_user_{i}',
        ) for i in range(1, 11)
    ]
    convert_tasks = [user_tool.convert_user_info(credential, 'user') for credential in user_credentials]
    users = await asyncio.gather(*convert_tasks)
    user_to_create = [User(
        id=i + 2,
        username=user.username,
        password=user.hashed_password,
        role=user.role,
    ) for i, user in enumerate(users)]
    await User.bulk_create(user_to_create)

async def delete_all_users():

    """delete all users except for the default admin"""

    await User.filter(username__not='admin').delete()

async def user_factory(user_credential: UserCredentials, role: Literal['user', 'admin', 'banned'], user_id: int):

    """create a user"""

    user_to_create = await user_tool.convert_user_info(user_credential, role)
    await User.create(
        id=user_id,
        username=user_to_create.username,
        password=user_to_create.hashed_password,
        role=user_to_create.role,
    )

async def user_destroy(username: str):

    """delete a user"""

    user = await User.get(username=username)
    await user.delete()

async def change_user_role(username: str, role: str):

    """change the role of a user"""

    user = await User.get(username=username)
    user.role = UserRole(role)
    await user.save()

async def init_problems():

    """initialize the 20 problems for testing"""

    init_tasks = [add_problem(f'p{i:03d}.json') for i in range(1, 21)]
    await asyncio.gather(*init_tasks)

async def add_problem(file_name: str):

    """add a problem into the database"""

    problem_dict = get_problem_dict(file_name)
    problem_schema = ProblemSchema(**problem_dict)
    problem = problem_parse.problem_schema_to_problem(problem_schema)
    await problem.save()

def get_problem_dict(file_name: str):

    """returns the problem dict in the corresponding file"""

    PROBLEM_PATH = os.path.join(os.curdir, 'tests', 'test_problem_set')
    with open(os.path.join(PROBLEM_PATH, file_name), 'r', encoding='utf-8') as f:
        content = f.read()
    return json.loads(content)

async def clear_problems():

    """clear all problems in the database"""

    await Problem.all().delete()

async def problem_exist(problem_id: str):

    """returns true if the problem exists in the database"""

    problem = await Problem.get_or_none(id=problem_id)
    if problem:
        return True
    return False

async def language_factory(lan: LanguageSchema, redis: AioRedis):

    """create a language in the database"""

    language = language_parse.language_schema_to_language(lan)
    await language.save()

    await redis.set(f'language:{lan.name}', lan.model_dump_json())

async def init_languages(redis: AioRedis):

    """create two supported languages in the database"""

    await language_factory(
        LanguageSchema(
            name='python',
            file_ext='py',
            compile_cmd=None,
            run_cmd='python {src}',
            image_name='python:3.12-slim',
        ),
        redis,
    )
    await language_factory(
        LanguageSchema(
            name='cpp',
            file_ext='cpp',
            compile_cmd='g++ {src} -o {exe}',
            run_cmd='{exe}',
            image_name='gcc:14.3.0',
        ),
        redis,
    )

async def clear_languages(redis: AioRedis):

    """clear all languages in the database and redis"""

    await Language.all().delete()
    await clear_redis_keys('language:*', redis)

async def clear_user_submission_timestamp(redis: AioRedis):
    
    """clear all user submission timestamps"""

    await clear_redis_keys('user_submission_timestamp:*', redis)

async def clear_redis_keys(prefix: str, redis: AioRedis):

    """clear all keys with the prefix"""

    cursor = 0
    redis_keys = []
    while True:
        cursor, keys = await redis.scan(
            cursor=cursor,
            match=prefix,
            count=1000,
        )
        redis_keys.extend(keys)
        if cursor == 0:
            break

    if redis_keys != []:
        await redis.delete(*redis_keys)

async def submission_factory(submission_data: SubmissionData):

    """create a submission"""

    submission, tests = submission_parse.parse_data_to_submission(submission_data)
    await submission.save()
    await Test.bulk_create(tests)
