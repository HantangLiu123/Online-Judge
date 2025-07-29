import aiosqlite
import math
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
                    submission_time DATETIME NOT NULL,
                    user_id INTEGER NOT NULL,
                    problem_id TEXT NOT NULL,
                    language TEXT NOT NULL,
                    status TEXT NOT NULL,
                    score INTEGER,
                    counts INTEGER,
                    code TEXT NOT NULL
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
                    (id, submission_time, user_id, problem_id, language, status, score, counts, code)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.submission_id,
                    result.submission_time,
                    result.user_id,
                    result.problem_id,
                    result.language,
                    result.status,
                    result.score,
                    result.counts,
                    result.code,
                ))
            except aiosqlite.IntegrityError:
                # the id is not unique
                return False
            await db.commit()
        return True
    
    async def update_submission(
        self,
        submission_id: str,
        status: str,
        score: int | None,
        counts: int | None
    ) -> None:

        """update the submission according to the parameters"""

        submission = await self.get_submission_by_id(submission_id)
        if submission is None:
            raise ValueError('The submission does not exist')
        
        # update the submission
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE submissions
                SET status = ?, score = ?, counts = ?
                WHERE id = ? 
            """, (status, score, counts, submission_id))
            await db.commit()

    def where_clause_submission_list(
        self,
        user_id: int | None = None,
        problem_id: str | None = None,
        status: str | None = None,
    ) -> tuple[str, list]:
        
        """makes the query for the get submission list function"""

        if user_id is None and problem_id is None:
            # one of them should not be none
            raise ValueError('one of the user_id and problem_id should not be None')
        # construct the where clause for the query
        conditions = []
        params = []
        if user_id is not None:
            conditions.append('user_id = ?')
            params.append(user_id)
        if problem_id is not None:
            conditions.append('problem_id = ?')
            params.append(problem_id)
        if status is not None:
            conditions.append('status = ?')
            params.append(status)
        where_clause = ' AND '.join(conditions)
        return where_clause, params

    async def get_submission_list(
        self,
        user_id: int | None = None,
        problem_id: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[int, list[dict]]:
        
        """the submission list filtered by the parameters
        
        This function returns the submission list filtered by user_id, problem_id, and/or status.
        At least one of the user_id or problem_id should not be none.
        """

        async with aiosqlite.connect(self.db_path) as db:
            # getting the total number of submissions
            where_clause, params = self.where_clause_submission_list(user_id, problem_id, status)
            cursor = await db.execute(f'SELECT COUNT(*) FROM submissions WHERE {where_clause}')
            res = await cursor.fetchone()
            if res is None:
                return 0, []
            
            total = res[0]
            # see if the page exceeds the max page
            total_pages = math.ceil(total / page_size)
            if page > total_pages and total_pages != 0:
                raise ValueError('the page num exceeds the max page number')
            
            # get the list
            offset = page_size * (page - 1)
            query = f"""
                SELECT id, status, score, counts FROM submissions
                WHERE {where_clause}
                ORDER BY submission_time DESC
                LIMIT ? OFFSET ?
            """
            query_params = params + [page_size, offset]
            cursor = await db.execute(query, query_params)
            submission_list = await cursor.fetchall()

            if not submission_list:
                return 0, []
            
            columns = [col[0] for col in cursor.description]
            return total, [dict(zip(columns, submission)) for submission in submission_list]

# create the instance
submissionResultManager = SubmissionResManager()
