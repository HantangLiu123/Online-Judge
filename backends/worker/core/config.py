import os

class Settings:

    """a class for extracting settings from environment variables"""

    def __init__(self):
        # getting each setting by env or a default value
        self.redis_host = os.getenv("REDIS_HOTS", "redis")
        self.max_jobs = int(os.getenv("MAX_JOBS", 5))

settings = Settings()
