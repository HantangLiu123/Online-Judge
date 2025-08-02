from pydantic import BaseModel, Field, StringConstraints
from typing import Literal, Annotated
from datetime import datetime, date

class Problem(BaseModel):

    """a base model for a problem in this online judge system"""

    # required elements, the min_length is for checking blank strings
    id: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1)
    input_description: str = Field(min_length=1)
    output_description: str = Field(min_length=1)
    samples: list[dict[str, str]]
    constraints: str = Field(min_length=1)
    testcases: list[dict[str, str]]

    # optional elements
    hint: str = ""
    source: str = ""
    tags: list[str] = []
    time_limit: float | None = Field(default=None, ge=0)
    memory_limit: int | None = Field(default=None, ge=0)
    author: str = ""
    difficulty: str = 'medium'

class User(BaseModel):

    """a base model for the sign in process"""

    username: str = Field(min_length=3, max_length=40)
    password: str = Field(min_length=5)
    role: Literal['user', 'admin', 'banned'] = 'user'

class NewRole(BaseModel):

    """a base model for setting an user to a new role"""

    role: Literal['user', 'admin', 'banned']

class ProblemSubmission(BaseModel):

    """a model for a submission of a problem"""

    problem_id: str = Field(min_length=1)
    language: str = Field(min_length=1)
    code: str = Field(min_length=1)

class Language(BaseModel):

    """a model for a coding language supported by this OJ app"""

    name: str = Field(min_length=1)
    file_ext: str = Field(min_length=1)
    compile_cmd: Annotated[str | None, StringConstraints(min_length=1)] = None
    run_cmd: str = Field(min_length=1)
    time_limit: float = Field(default=1.0, ge=0)
    memory_limit: int = Field(default=128, ge=0)

class SubmissionResult(BaseModel):

    """a model for a submission result"""

    submission_id: str
    submission_time: datetime
    user_id: int
    problem_id: str
    language: str
    status: str
    score: int | None = None
    counts: int | None = None
    code: str

class SubmissionTestDetail(BaseModel):

    """a model for recording a test detail"""

    id: int
    result: str
    time: float
    memory: int

class SubmissionPostModel(BaseModel):

    """a model for a user to submit with a post request"""

    problem_id: str = Field(min_length=1)
    language: str = Field(min_length=1)
    code: str = Field(min_length=1)

class UserData(BaseModel):

    """the complete version of user (for importing data)"""

    id: int = Field(ge=1)
    username: str = Field(min_length=3, max_length=40)
    password: str = Field(min_length=5) # hashed
    role: Literal['user', 'admin', 'banned']
    join_time: date
    submit_count: int = Field(ge=0)
    resolve_count: int = Field(ge=0)

class SubmissionData(BaseModel):

    """the export/import data version of a submission"""

    id: str = Field(min_length=1)
    submission_time: datetime
    user_id: int = Field(ge=1)
    problem_id: str = Field(min_length=1)
    language: str = Field(min_length=1)
    status: Literal['success', 'pending', 'error']
    score: int | None = None
    counts: int | None = None
    code: str = Field(min_length=1)
    details: list[SubmissionTestDetail]

class ResolveData(BaseModel):

    """the model for a line in the resolves table"""

    problem_id: str = Field(min_length=1)
    user_id: int = Field(ge=1)
    language: str = Field(min_length=1)
    resolved: bool

class ImportData(BaseModel):

    """the model for a standard importing data"""

    users: list[UserData]
    problems: list[Problem]
    submissions: list[SubmissionData]
    resolves: list[ResolveData]
    languages: list[Language]
    