from pydantic import BaseModel
from typing import Literal

class LoginResponse(BaseModel):

    """a model for the login response"""

    user_id: int
    username: str
    role: Literal['user', 'admin', 'banned']
