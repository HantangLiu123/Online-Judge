import os
import logging.config

class Settings:

    """a class for extracting the settings from the environment variable"""

    def __init__(self) -> None:
        # getting all the settings either from env or using a default value
        self.app_name = os.getenv("APP_NAME", "api")
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.secret_key = os.getenv("SECRET_KEY")
        self.token_max_age = int(os.getenv("TOKEN_MAX_AGE", "7200")) # max age in seconds
        self.same_site = os.getenv("SAME_SITE", "lax")
        self.token_http_only = os.getenv("TOKEN_HTTP_ONLY", "False").lower() == "true"
        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.redis_host = os.getenv("REDIS_HOTS", "redis")
        self.secure = os.getenv("SECURE", "False").lower == "true"

        if not self.secret_key:
            raise ValueError("Please set your jwt secret key")
        
settings = Settings()

# the config of uvicorn logger (from chatgpt 5)
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "default": {
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        },
        "access": {
            "format": "%(asctime)s - %(levelname)s - %(message)s",
        },
        "user_access": {
            "format": "%(asctime)s - %(levelname)s - %(message)s", 
        },
        "debug": {
            "format": "%(asctime)s - %(levelname)s - %(message)s",
        }
    },

    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "access": {
            "class": "logging.StreamHandler",
            "formatter": "access",
            "stream": "ext://sys.stdout",
        },
        "user_access": {
            "class": "logging.StreamHandler",
            "formatter": "user_access",
            "stream": "ext://sys.stdout",
        },
        "debug": {
            "class": "logging.StreamHandler",
            "formatter": "debug",
            "stream": "ext://sys.stdout",
        }
    },

    "loggers": {
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["access"],
            "propagate": False,
        },
        "user_access": {
            "level": "INFO",
            "handlers": ["user_access"],
            "propagate": False,
        },
        "debug": {
            "level": "DEBUG",
            "handlers": ["debug"],
            "propagate": False,
        }
    },
}

def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
