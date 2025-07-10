import aiosqlite
from ..config import settings
import bcrypt

class UserManager:

    """a class for managing user database"""

    def __init__(self):
        self.db_path = settings.database_path

    async def create_users_table(self):

        """create the user table if the table is not created yet"""

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    join_time DATETIME NOT NULL,
                    submit_count INTEGER DEFAULT 0,
                    resolve_count INTEGER DEFAULT 0
                )
            """)

    async def get_user(self, user_id: int):

        """find the user by his/her id"""

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT * FROM users
                WHERE id = ?
            """, (user_id, ))
            user_row = await cursor.fetchone()
            columns = [col[0] for col in cursor.description]
            user_dict = dict(zip(columns, user_row)) # type: ignore

        return user_dict
    