from typing_extensions import Annotated, Doc
from fastapi import Request, HTTPException, status
from typing import Any, Dict
from ..core.security.SessionManager import SessionManager, AuthenticationError

def get_current_user(request: Request) -> dict[str, Any]:

    """packaging get_current_user in SessionManager"""

    user = SessionManager.get_current_user(request)
    if not user:
        raise AuthenticationError
    return user

class UnexpectedError(HTTPException):
    
    """unexpected error that could be triggered"""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unexpected error",
        )
