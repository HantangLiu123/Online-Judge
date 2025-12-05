from arq.connections import RedisSettings
from .core.config import settings
from .utils import image, judge

REDIS_SETTINGS = RedisSettings(host=settings.redis_host)

class DownloadImageSettings:

    """settings for workers to download images"""

    functions = [image.pull_image]
    on_startup = image.startup
    on_shutdown = image.shutdown
    redis_settings = REDIS_SETTINGS

class JudgeSettings:

    """settings for workers to of judge process"""

    functions = [judge.judge_task]
    on_startup = judge.startup
    on_shutdown = judge.shutdown
    redis_settings = REDIS_SETTINGS
