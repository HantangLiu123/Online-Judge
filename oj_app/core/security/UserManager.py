import aiosqlite
from ..config import settings
import bcrypt
from datetime import date
from oj_app.models.schemas import User
import math

class UserManager:

    """a class for managing user database"""

    def __init__(self):
        self.db_path = settings.database_path

    async def create_user_table(self):

        """create the user table if the table is not created yet"""

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    join_time DATETIME NOT NULL,
                    submit_count INTEGER DEFAULT 0,
                    resolve_count INTEGER DEFAULT 0
                )
            """)
            await db.commit()

    async def get_user_by_id(self, user_id: int) -> dict | None:

        """find the user by his/her id"""

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT * FROM users
                WHERE id = ?
            """, (user_id, ))
            user_row = await cursor.fetchone()
            if user_row is None:
                return None

            columns = [col[0] for col in cursor.description]
            user_dict = dict(zip(columns, user_row))

        return user_dict
    
    async def get_user_by_username(self, username: str) -> dict | None:

        """find the user by his/her username"""

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT * FROM users
                WHERE username = ?
            """, (username, ))
            user_row = await cursor.fetchone()
            if user_row is None:
                return None

            columns = [col[0] for col in cursor.description]
            user_dict = dict(zip(columns, user_row))

        return user_dict

    async def username_match_password(self, username: str, password: str) -> bool:

        """check if the username and the password matched"""

        user = await self.get_user_by_username(username)
        if user is None:
            return False
        return bcrypt.checkpw(password=password.encode(), hashed_password=user['password'].encode())

    async def create_user(self, new_user: User) -> int | None:

        """create the user according to the user dict"""

        # check if the id is already existed
        user = await self.get_user_by_username(new_user.username)
        if user is not None:
            raise ValueError("Username already existed")

        # get the date
        join_date = date.today()

        #incrypt the password
        password = new_user.password.encode()
        hashed_password = bcrypt.hashpw(password=password, salt=bcrypt.gensalt()).decode()

        # store in the data base
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO users (username, password, role, join_time)
                VALUES (?, ?, ?, ?)
            """, (new_user.username, hashed_password, new_user.role, join_date))
            await db.commit()
            return cursor.lastrowid
        
    async def change_user_role(self, user_id: int, new_role: str) -> tuple[int, str]:

        """set the user with the user_id to his/her new role"""

        # check if the user exists
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise ValueError("User with the id does not exist")

        async with aiosqlite.connect(self.db_path) as db:
            # update the role
            await db.execute(
                "UPDATE users SET role = ? WHERE id = ?",
                (new_role, user_id)
            )
            await db.commit()

            # return the id and the role
            return user_id, new_role
        
    async def add_submit_count(self, user_id: int):

        """add the user's submit count"""

        #check if the user exists
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise ValueError("User with the id does not exist")
        
        async with aiosqlite.connect(self.db_path) as db:
            # update the submit count
            await db.execute(
                "UPDATE users SET submit_count = ? WHERE id = ?",
                (user['submit_count'] + 1, user_id)
            )
            await db.commit()

            return user_id, user['submit_count'] + 1
        
    async def add_resolve_count(self, user_id: int):

        """add the user's resolve count"""

        #check if the user exists
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise ValueError("User with the id does not exist")
        
        async with aiosqlite.connect(self.db_path) as db:
            # update the resolve count
            await db.execute(
                "UPDATE users SET resolve_count = ? WHERE id = ?",
                (user['resolve_count'] + 1, user_id)
            )
            await db.commit()

            return user_id, user['resolve_count'] + 1
        
    async def get_users(self, page: int, page_size: int) -> tuple[int, list]:

        """get user information according to the page and the page size"""

        async with aiosqlite.connect(self.db_path) as db:

            # getting the total number of users
            cursor = await db.execute('SELECT COUNT(*) FROM users')
            res = await cursor.fetchone()
            assert res is not None # there should be at least one default admin
            total = res[0]

            # see if the page num exceeds the max page
            total_pages = math.ceil(total / page_size)
            if page > total_pages and total_pages != 0:
                raise ValueError('the page number exceeds the max page')
            
            # get the user list
            offset = (page - 1) * page_size
            cursor = await db.execute("""
                SELECT id, username, join_time, submit_count, resolve_count FROM users
                ORDER BY id LIMIT ? OFFSET ?
            """, 
            (page_size, offset))
            user_list = await cursor.fetchall()

            if not user_list:
                return total, []
            columns = [col[0] for col in cursor.description]
            return total, [dict(zip(columns, user)) for user in user_list]
        
# initailyze a UserManager instance
userManager = UserManager()
    