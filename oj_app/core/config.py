from dotenv import load_dotenv
import os
import logging

class Settings:

    """a class for extracting the settins from .env"""

    def __init__(self) -> None:
        load_dotenv()

        # getting all the settings either from dotenv or using a default value
        self.app_name = os.getenv("APP_NAME", "api")
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.secret_key = os.getenv("SECRET_KEY")
        self.session_max_age = int(os.getenv("SESSION_MAX_AGE", "7200")) # max age in seconds
        self.same_site = os.getenv("SAME_SITE", "lax")
        self.session_https_only = os.getenv("SESSION_HTTPS_ONLY", "False").lower() == "true"
        self.database_path = os.getenv("DATABASE_PATH", os.path.join(os.pardir, "db.sqlite3"))
        self.log_path = os.getenv("LOG_PATH", os.path.join(os.pardir, "log"))
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost")
        self.max_workers = int(os.getenv("MAX_WORKERS", 5))

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

        # log about supported languages
        self.language_logger = logging.getLogger('langauge')
        self.language_logger.setLevel(logging.INFO)
        language_handler = logging.FileHandler(os.path.join(self.LOG_DIR, 'language.log'))
        language_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.language_logger.addHandler(language_handler)
        self.language_logger.propagate = False

        # log about the task queue
        self.queue_logger = logging.getLogger('queue')
        self.queue_logger.setLevel(logging.INFO)
        queue_handler = logging.FileHandler(os.path.join(self.LOG_DIR, 'queue.log'))
        queue_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.queue_logger.addHandler(queue_handler)
        self.queue_logger.propagate = False

        # log about data
        self.data_logger = logging.getLogger('data')
        self.data_logger.setLevel(logging.INFO)
        data_handler = logging.FileHandler(os.path.join(self.LOG_DIR, 'data.log'))
        data_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.data_logger.addHandler(data_handler)
        self.data_logger.propagate = False

    def write_user_management_log(self, message: str) -> None:

        """use for backgroundtasks"""

        self.user_management_logger.info(message)

    def write_problem_management_log(self, message: str) -> None:

        """use for backgroundtasks"""

        self.problem_management_logger.info(message)

    def write_language_log(self, message: str) -> None:

        """use for background tasks"""

        self.language_logger.info(message)

    def queue_info_log(self, message: str) -> None:

        """record info in queue log"""

        self.queue_logger.info(message)

    def queue_error_log(self, message: str) -> None:

        """record error in queue log"""

        self.queue_logger.error(message)

    def write_data_log(self, message: str) -> None:

        """use for background tasks"""

        self.data_logger.info(message)

    def remove_all_log(self) -> None:
        for file in os.listdir(self.LOG_DIR):
            open(os.path.join(self.LOG_DIR, file), 'w').close()

logs = Logs()
