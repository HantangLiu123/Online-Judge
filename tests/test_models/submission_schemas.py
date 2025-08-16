from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class GetSubmissionModel(BaseModel):

    """a model for getting a submission"""

    status: Literal['pending', 'success', 'error']
    score: int | None = None
    counts: int | None = None

class SubmissionListSnippet(BaseModel):

    """a model of a submission list snippet"""

    id: str
    status: Literal['pending', 'success', 'error']
    score: int | None = None
    counts: int | None = None

class SubmissionList(BaseModel):

    """a model of a submission list"""

    total: int
    submissions: list[SubmissionListSnippet]

class SubmissionInfo(BaseModel):

    """a model for the submission info"""

    id: str = Field(min_length=1)
    submission_time: datetime
    user_id: int = Field(ge=1)
    problem_id: str = Field(min_length=1)
    language: str = Field(min_length=1)
    status: Literal['success', 'pending', 'error']
    score: int | None = None
    counts: int | None = None
    code: str = Field(min_length=1)

class TestCase(BaseModel):

    """a model of the submission test case"""

    id: int
    result: Literal['AC', 'WA', 'CE', 'RE', 'TLE', 'MLE', 'UNK']
    time: float
    memory: int

class SubmissionLog(BaseModel):

    """a model of the submission log"""

    submission: SubmissionInfo
    details: list[TestCase]
