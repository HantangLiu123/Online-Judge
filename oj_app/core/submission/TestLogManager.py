import aiosqlite
from ..config import settings
from oj_app.models.schemas import SubmissionTestDetail

class TestLogManager:

    """a class to manage the submission logs"""

    def __init__(self) -> None:
        self.db_path = settings.database_path

    async def create_test_log_tables(self) -> None:

        """create tables for test logs"""

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tests(
                    submission_id TEXT NOT NULL,
                    id INTEGER NOT NULL,
                    result TEXT NOT NULL,
                    time REAL NOT NULL,
                    memory INTEGER NOT NULL,
                    PRIMARY KEY (submission_id, id)
                )
            """)
            await db.commit()

    async def get_log(self, submission_id: str, sample_id: int) -> dict | None:

        """get a test log with the submission_id and the sample_id"""

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT * FROM tests WHERE submission_id = ? AND id = ?',
                (submission_id, sample_id),
            )
            test_log = await cursor.fetchone()
            if test_log is None:
                # can't find the log
                return None
            
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, test_log))
        
    async def get_logs(self, submission_id: str) -> list[dict] | None:

        """get test logs according to the submission_id"""

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT * FROM tests WHERE submission_id = ?',
                (submission_id, ),
            )
            test_logs = await cursor.fetchall()
            if test_logs is None:
                # can't find any log with the submission_id
                return None
            
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, test_log)) for test_log in test_logs]
        
    async def insert_logs(self, submission_id: str, test_logs: list[SubmissionTestDetail]) -> None:

        """insert the test logs into the table"""

        async with aiosqlite.connect(self.db_path) as db:
            try:
                for test_log in test_logs:
                    await db.execute(
                        """
                        INSERT INTO tests
                        (submission_id, id, result, time, memory)
                        VALUES(?, ?, ?, ?, ?)
                        """,
                        (
                            submission_id,
                            test_log.sample_id,
                            test_log.result,
                            test_log.time,
                            test_log.memory,
                        ),
                    )
            except aiosqlite.IntegrityError:
                raise ValueError('conflict primary key in tests table')
            await db.commit()

    async def change_logs(self, submission_id: str, new_logs: list[SubmissionTestDetail]) -> None:

        """change the logs"""

        async with aiosqlite.connect(self.db_path) as db:
            for new_log in new_logs:
                old_log = await self.get_log(submission_id, new_log.sample_id)
                if old_log is None:
                    raise ValueError('cannot change the log since it does not exist')
                await db.execute(
                    """
                    UPDATE tests
                    SET result = ?, time = ?, memory = ?
                    WHERE submission_id = ? AND id = ?
                    """,
                    (
                        new_log.result,
                        new_log.time,
                        new_log.memory,
                        submission_id,
                        new_log.sample_id,
                    ),
                )
            await db.commit()

# create the instance
testLogManager = TestLogManager()
