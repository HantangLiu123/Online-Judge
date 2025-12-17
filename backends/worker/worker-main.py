from arq.connections import RedisSettings
from arq.worker import Worker
from .core.config import settings
from .utils import image, judge

REDIS_SETTINGS = RedisSettings(host=settings.redis_host)

class OJSettings:

    """settings for workers to download images"""

    functions = [image.pull_image, judge.judge_task]
    on_startup = judge.startup
    on_shutdown = judge.shutdown
    redis_settings = REDIS_SETTINGS
    max_jobs = settings.max_jobs
