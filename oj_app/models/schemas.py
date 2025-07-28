from pydantic import BaseModel, Field, StringConstraints
from typing import Literal, Annotated

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
    difficulty: str = '中等'

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
    user_id: int
    problem_id: int
    language: str
    status: str
    score: int
    counts: int
    code: str

class SubmissionTestDetail(BaseModel):

    """a model for recording a test detail"""

    sample_id: int
    result: str
    time: float
    memory: int
