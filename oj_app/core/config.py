from dotenv import load_dotenv
import os
from typing import Literal

class Settings:

    """a class for extracting the settins from .env"""

    def __init__(self) -> None:
        load_dotenv()

        # getting all the settings either from dotenv or using a default value
        self.app_name = os.getenv("APP_NAME", "api")
        self.debug = os.getenv("DEBUG", "False").lower == "true"
        self.secret_key = os.getenv("SECRET_KEY")
        self.session_max_age = int(os.getenv("SESSION_MAX_AGE", "7200")) # max age in seconds
        self.same_site = os.getenv("SAME_SITE", "lax")
        self.session_https_only = os.getenv("SESSION_HTTPS_ONLY", "False").lower() == "true"
        self.database_path = os.getenv("DATABASE_PATH", os.path.join(os.pardir, "db.sqlite3"))

        if not self.secret_key:
            raise ValueError("Please set your session secret key")

settings = Settings()
