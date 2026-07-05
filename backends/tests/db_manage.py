import asyncio
from tortoise import Tortoise
from redis import asyncio as aioredis
from .settings import TORTOISE_ORM
from . import utils

async def init_db():

    """initialize the database for testing"""

    await Tortoise.init(TORTOISE_ORM)
    redis = aioredis.from_url('redis://localhost:6379/0')
    await utils.delete_all_users()
    await utils.clear_problems()
    await utils.clear_languages(redis)
    await utils.init_problems()
    await utils.test_init_small()
    await utils.init_languages(redis)
    await redis.close()
    await redis.connection_pool.disconnect()  # type: ignore
    await Tortoise.close_connections()

async def clear_db():

    """clear all data in the database after testing"""

    await Tortoise.init(TORTOISE_ORM)
    redis = aioredis.from_url('redis://localhost:6379/0')
    await utils.delete_all_users()
    await utils.clear_problems()
    await utils.clear_languages(redis)
    await redis.close()
    await redis.connection_pool.disconnect()  # type: ignore
    await Tortoise.close_connections()

if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'init':
        asyncio.run(init_db())
    elif sys.argv[1] == 'clear':
        asyncio.run(clear_db())
        