from fastapi import Request
from typing import Any
from Online_Judge.oj_app.core.security.SessionManager import SessionManager, AuthenticationError

def get_current_user(request: Request) -> dict[str, Any]:

    """packaging get_current_user in SessionManager"""

    user = SessionManager.get_current_user(request)
    if not user:
        raise AuthenticationError
    return user
