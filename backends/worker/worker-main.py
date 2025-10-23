from arq import create_pool
from arq.connections import RedisSettings
from .core.config import settings
from .utils import image

REDIS_SETTINGS = RedisSettings(host=settings.redis_host)

class DownloadImageSettings:

    """settings for workers to download images"""

    functions = [image.pull_image]
    on_startup = image.startup
    on_shutdown = image.shutdown
    redis_settings = REDIS_SETTINGS
