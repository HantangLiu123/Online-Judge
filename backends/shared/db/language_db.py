import asyncio
import json
from redis.asyncio import Redis as AioRedis
from tortoise.exceptions import IntegrityError
from ..models import Language
from ..schemas import LanguageSchema
from ..utils import language_parse

async def get_language(lan_name: str, redis: AioRedis) -> LanguageSchema | None:

    """returns the corresponding language schema"""

    if not lan_name.startswith('language:'):
        # for normal usage (in api/worker)
        key_name = f'language:{lan_name}'
    else:
        # for the get_all_languages
        key_name = lan_name
    lan_content = await redis.get(key_name)
    if lan_content is None:
        return None
    lan_dict = json.loads(lan_content)
    language = LanguageSchema(**lan_dict)
    return language

async def get_all_languages(redis: AioRedis) -> list[LanguageSchema]:

    """returns all language dict in a list"""

    key_pattern = 'language:*'
    cursor = 0
    lan_keys: list[bytes] = []

    # find the keys
    while True:
        cursor, keys = await redis.scan(
            cursor=cursor,
            match=key_pattern,
            count=100,
        )
        lan_keys.extend(keys)
        if cursor == 0:
            break

    # get the languages
    get_tasks = [get_language(lan.decode(), redis) for lan in lan_keys]
    lan_sche = await asyncio.gather(*get_tasks)
    return lan_sche # type: ignore since there must be value saved for existed keys

async def create_language_in_db(lan: LanguageSchema, redis: AioRedis) -> bool:

    """create the language in the database
    
    This function returns true if the process succeeds,
    returns false if it fails
    """

    language = language_parse.language_schema_to_language(lan)
    try:
        await language.save()
    except IntegrityError:
        return False
    
    # add the language to the redis
    await redis.set(f'language:{lan.name}', lan.model_dump_json())
    return True

async def init_lan_in_redis(redis: AioRedis):

    """put all languages in the database into redis"""

    languages = await Language.all()
    lans = [language_parse.language_to_language_schema(language) for language in languages]
    init_tasks = [redis.set(f'language:{lan.name}', lan.model_dump_json()) for lan in lans]
    await asyncio.gather(*init_tasks)

async def reset_language_table(redis: AioRedis):

    """reset the language table and the redis"""

    await Language.all().delete()
    cursor = 0
    while True:
        cursor, keys = await redis.scan(
            cursor=cursor,
            match='language:*',
            count=100,
        )
        await redis.delete(*keys)
        if cursor == 0:
            break

async def export_language_table():

    """export all languages in the table"""

    return Language.all()

async def import_language_in_db(languages: list[Language]):

    """import languages in the database"""

    await Language.bulk_create(languages, ignore_conflicts=True)
