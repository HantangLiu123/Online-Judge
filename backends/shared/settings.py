import os

TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': os.getenv('DB_HOST', 'ojdb'),
                'port': int(os.getenv('DB_PORT', 5432)),
                'user': os.getenv('DB_USER', 'oj_user'),
                'password': os.getenv('DB_PASSWORD', 'oj_password'),
                'database': os.getenv('DB_NAME', 'oj_app'),
                'minsize': int(os.getenv('DB_POOL_MINSIZE', 5)),
                'maxsize': int(os.getenv('DB_POOL_MAXSIZE', 20)),
                'max_queries': int(os.getenv('DB_MAX_QUERIES', 50000)),
                'timeout': float(os.getenv('DB_TIMEOUT', 30.0)),
                'command_timeout': float(os.getenv('DB_COMMAND_TIMEOUT', 60.0)),
            }
        }
    },
    'apps': {
        'models': ['shared.models', 'aerich.models'],
        'default_connection': 'default'
    }
}
