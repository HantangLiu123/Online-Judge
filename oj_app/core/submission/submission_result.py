import aiosqlite
from ..config import settings
from oj_app.models.schemas import SubmissionResult

class SubmissionResManager:

    """a class to manage the submission result"""

    def __init__(self) -> None:
        self.db_path = settings.database_path

    async def create_submission_table(self) -> None:

        """create the submission table if not exists"""

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS submissions (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    problem_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    counts INTEGER NOT NULL
                )
            """)
            await db.commit()

    async def get_submission_by_id(self, submission_id: str) -> dict | None:

        """get the submission result by its id"""
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT * FROM submissions WHERE id = ?", (submission_id, ))
            submission_row = await cursor.fetchone()
            if submission_row is None:
                return None
            
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, submission_row))

    async def insert_submission(self, result: SubmissionResult) -> bool:

        """insert the submission result according to the result model.
        
        It returns true if the insertion success, return false if it fails.
        """

        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("""
                    INSERT INTO submissions 
                    (id, user_id, problem_id, status, score, counts)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    result.submission_id,
                    result.user_id,
                    result.problem_id,
                    result.status,
                    result.score,
                    result.counts,
                ))
            except aiosqlite.IntegrityError:
                # the id is not unique
                return False
            await db.commit()
        return True
    
    async def update_submission(self, result: SubmissionResult) -> None:

        """update the submission according to the result"""

        submission = await self.get_submission_by_id(result.submission_id)
        if submission is None:
            raise ValueError('The submission does not exist')
        
        # these should not happen
        assert submission['user_id'] == result.user_id
        assert submission['problem_id'] == result.problem_id
        assert submission['counts'] == result.counts
        
        # update the submission
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE submissions
                SET status = ?, score = ?
                WHERE id = ? 
            """, (result.status, result.score, result.submission_id))
            await db.commit()
