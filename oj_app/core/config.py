from dotenv import load_dotenv
import os
import logging

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
        self.log_path = os.getenv("LOG_PATH", os.path.join(os.pardir, "log"))

        if not self.secret_key:
            raise ValueError("Please set your session secret key")

settings = Settings()

class Logs:
    def __init__(self) -> None:
        self.LOG_DIR = settings.log_path

        # log about user management
        self.user_management_logger = logging.getLogger('user_management')
        self.user_management_logger.setLevel(logging.INFO)
        user_management_handler = logging.FileHandler(os.path.join(self.LOG_DIR, 'user_management.log'))
        user_management_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.user_management_logger.addHandler(user_management_handler)
        self.user_management_logger.propagate = False

        # log about problem management
        self.problem_management_logger = logging.getLogger('problem_management')
        self.problem_management_logger.setLevel(logging.INFO)
        problem_management_handler = logging.FileHandler(os.path.join(self.LOG_DIR, 'problem_management.log'))
        problem_management_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.problem_management_logger.addHandler(problem_management_handler)
        self.problem_management_logger.propagate = False

    def write_user_management_log(self, message: str) -> None:

        """use for backgroundtasks"""

        self.user_management_logger.info(message)

    def write_problem_management_log(self, message: str) -> None:

        """usr for backgroundtasks"""

        self.problem_management_logger.info(message)

logs = Logs()
