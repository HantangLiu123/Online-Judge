from pydantic import BaseModel

from typing import Literal

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

    users: list[UserInList]
