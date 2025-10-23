from typing import Any
import aiodocker
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from arq.connections import ArqRedis

async def startup(ctx: dict[Any, Any]):

    """init the aiodocker client, redis client and fastapi cache
    for the pull image worker
    """

    ctx['docker_client'] = aiodocker.Docker()
    FastAPICache.init(RedisBackend(ctx['redis']), prefix='fastapi-cache')

async def shutdown(ctx: dict[Any, Any]):

    """close the aiodocker client"""

    await ctx['docker_client'].close()

async def pull_image(ctx: dict[Any, Any], image_name: str):

    """pull the image according to the name"""

    docker: aiodocker.Docker = ctx['docker_client']
    redis: ArqRedis = ctx['redis']
    
    # pull the image with progression status
    async for progress in docker.images.pull(image_name, stream=True):
        if 'progressDetail' in progress:
            detail = progress['progressDetail']
            if 'current' in detail and 'total' in detail and detail['total'] > 0:
                percent = detail['current'] / detail['total'] * 100
                await redis.set(f'download:image:{image_name}', percent)
