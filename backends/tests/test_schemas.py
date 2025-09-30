from pydantic import BaseModel, Field
from typing import Literal
from shared.schemas import ProbCase

class LoginResponse(BaseModel):

    """a model for the login response"""

    user_id: int
    username: str
    role: Literal['user', 'admin', 'banned']

class UserSignIn(BaseModel):

    """a model for the user sign in response"""

    user_id: int

class CreateAdmin(BaseModel):

    """a model for the admin create response"""

    user_id: int
    username: str

class UserInfo(BaseModel):

    """a model for the response of get user info"""

    user_id: int
    username: str
    join_time: str
    role: Literal['user', 'admin', 'banned']
    submit_count: int
    resolve_count: int

class ChangeRole(BaseModel):

    """a model for the response of change user role"""

    user_id: int
    role: Literal['user', 'admin', 'banned']

class UserInList(BaseModel):

    """a model for a user in the user list"""

    id: int
    username: str
    role: Literal['user', 'admin', 'banned']
    join_time: str
    submit_count: int
    resolve_count: int

class UserList(BaseModel):

    """a model for the response of the get user list"""

    total: int
    total_page: int
    users: list[UserInList]

class ProblemSnippet(BaseModel):

    """a model for a snippet of a problem in the problem list"""

    id: str
    title: str

class ProblemList(BaseModel):

    """a model for the responst of get problem list"""

    total: int
    total_page: int
    problems: list[ProblemSnippet]

class ProblemSchemaUser(BaseModel):

    """the format of what the user can see in a problem (without the testcases)"""

    # required elements, the min_length is for checking blank strings
    id: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1)
    input_description: str = Field(min_length=1)
    output_description: str = Field(min_length=1)
    samples: list[ProbCase] = Field(min_length=1)
    constraints: str = Field(min_length=1)

    # optional elements
    hint: str = ""
    source: str = ""
    tags: list[str] = []
    time_limit: float | None = Field(default=None, ge=0)
    memory_limit: int | None = Field(default=None, ge=0)
    author: str = ""
    difficulty: str = 'medium'
