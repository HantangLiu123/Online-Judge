from fastapi import Request, HTTPException, status
from typing import Any

class SessionManager:

    @staticmethod
    def create_session(request: Request, user_data: dict[str, Any]) -> None:

        """create the session for the user"""

        request.session['user_id'] = user_data['user_id']
        request.session['username'] = user_data['username']
        request.session['role'] = user_data['role']

    @staticmethod
    def get_current_user(request: Request) -> dict[str, Any] | None:

        """identify the user from its session"""

        user_id = request.session.get('user_id')
        if not user_id:
            return None
        return {
            'user_id': user_id,
            'username': request.session['username'],
            'role': request.session['role']
        }
    
    @staticmethod
    def delete_session(request: Request) -> None:

        """delete the session, normally used when the user is logging off"""

        request.session.clear()
    
class AuthenticationError(HTTPException):
    
    """not logged in"""

    def __init__(self, detail: str = "not logged in") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
