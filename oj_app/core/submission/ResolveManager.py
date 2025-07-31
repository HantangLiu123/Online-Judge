import aiosqlite
from ..config import settings

class ResolveManager:

    """this class controls the table that stores which user resolve which problem"""

    def __init__(self) -> None:
        self.db_path = settings.database_path

    async def create_resolve_table(self) -> None:

        """create the resolve relation table if not exists"""

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS resolves(
                    problem_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    language TEXT NOT NULL,
                    resolved INTEGER NOT NULL,
                    PRIMARY KEY (problem_id, user_id, language)
                )
                """
            )
            await db.commit()

    async def find_resolve_relation(
        self,
        problem_id: str,
        user_id: int,
        language: str,
    ) -> bool | None:

        """get the resolve relation between the problem id and the user id"""

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                    SELECT resolved FROM resolves 
                    WHERE problem_id = ? AND user_id = ? AND language = ?
                """,
                (problem_id, user_id, language),
            )
            resolved = await cursor.fetchone()
            if resolved is None:
                # cannot find the relation
                return None
            return bool(resolved[0])
        
    async def insert_relation(
        self,
        problem_id: str,
        user_id: int,
        language: str,
        resolved: bool,
    ) -> None:

        """insert the relation"""

        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    """
                    INSERT INTO resolves
                    (problem_id, user_id, language, resolved)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        problem_id,
                        user_id,
                        language,
                        int(resolved),
                    )
                )
            except aiosqlite.IntegrityError:
                # the primary key has conflict
                raise ValueError('the primary key of the table resolves have conflict')
            await db.commit()

    async def update_relation(
        self,
        problem_id: str,
        user_id: int,
        language: str,
        resolved: bool,
    ) -> None:

        """update the relation"""

        old_relation = await self.find_resolve_relation(problem_id, user_id, language)
        if old_relation is None:
            raise ValueError('No relation found in this pair of problem and user')
        if old_relation == resolved:
            # no need to change
            return
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                    UPDATE resolves SET resolved = ? 
                    WHERE problem_id = ? AND user_id = ? AND language = ?
                """,
                (int(resolved), problem_id, user_id, language),
            )
            await db.commit()

resolveManager = ResolveManager()
