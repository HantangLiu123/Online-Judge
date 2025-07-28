import asyncio
import json
import uuid
import time
from datetime import datetime
from redis import asyncio as aioredis

class JudgeQueue:

    """a class for managing the judging queue"""

    def __init__(self, redis: aioredis.Redis, max_workers: int) -> None:
        self.redis = redis
        self.max_workers = max_workers
        self.running_tasks: dict[str, str] = {}
        
