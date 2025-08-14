import requests
import json
from redis import asyncio as aioredis

def print_response(response: requests.Response) -> None:
    print(response.status_code)
    formatted_content = json.dumps(response.json(), indent=4, ensure_ascii=False)
    print(formatted_content)
    print()

async def clear_api_cache(redis: aioredis.Redis) -> None:

    """clear the cache in the api"""

    # get all cache keys
    cursor = 0
    cache_keys = []
    while True:
        cursor, keys = await redis.scan(
            cursor=cursor,
            match='fastapi-cache:*',
            count=1000,
        )
        cache_keys.extend(keys)
        if cursor == 0:
            break
    
    # delete according to keys
    if cache_keys != []:
        await redis.delete(*cache_keys)

async def get_api_cache_keys(redis: aioredis.Redis, format: str) -> list:

    """get the keys in the api cache according to the format"""

    cursor = 0
    related_keys = []
    while True:
        cursor, keys = await redis.scan(
            cursor=cursor,
            match=format,
            count=1000,
        )
        related_keys.extend(keys)
        if cursor == 0:
            break

    return related_keys
