from pydantic import BaseModel
from typing import Literal
from datetime import date

class UserSignInResponse(BaseModel):

    """a model for the user sign in response"""

    user_id: int

class AdminCreateResponse(BaseModel):

    """a model for the admin create response"""

    user_id: int
    username: str

class UserInfoResponse(BaseModel):

    """a model for the user info response"""

    user_id: int
    username: str
    role: Literal['user', 'admin', 'banned']

class ChangeRoleResponse(BaseModel):

    """a model fo the change role response"""

    user_id: int
    role: Literal['user', 'admin', 'banned']

class UserListSnippet(BaseModel):

    """a model for one user in the user list"""

    id: int
    username: str
    join_time: date
    submit_count: int
    resolve_count: int

class UserListResponse(BaseModel):

    """a model for the user list response"""

    total: int
    users: list[UserListSnippet]
