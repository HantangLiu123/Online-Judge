from fastapi import status, Response, APIRouter, Request, BackgroundTasks
from oj_app.models.schemas import User
from oj_app.core.security.SessionManager import SessionManager
from oj_app.core.security.UserManager import userManager
from oj_app.core.config import logs
from oj_app.dependencies import common
from pydantic import ValidationError

router = APIRouter(prefix='/auth')

@router.post('/login')
async def user_login(request: Request, response: Response, user: dict, background_tasks: BackgroundTasks):

    """log in the user with the right username and password"""

    try:
        user_to_login = User(**user)
    except ValidationError:
        # the parameter format is wrong
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'code': status.HTTP_400_BAD_REQUEST,
            'msg': 'the parameter format is wrong',
            'data': None,
        }
    else:
        
        # get the user info
        user_logging_in = await userManager.get_user_by_username(
            username=user_to_login.username
        )

        if not user_logging_in:
            # the user does not exist
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return {
                'code': status.HTTP_401_UNAUTHORIZED,
                'msg': 'the username or password is incorrect',
                'data': None,
            }
        
        # check the username and password exist and correct
        if not await userManager.match_password(
            password=user_to_login.password,
            hashed_password=user_logging_in['password']
        ):
            # the password is incorrect
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return {
                'code': status.HTTP_401_UNAUTHORIZED,
                'msg': 'the username or password is incorrect',
                'data': None,
            }

        if user_logging_in['role'] == 'banned':
            # deny the log in request since the user is banned
            response.status_code = status.HTTP_403_FORBIDDEN
            return {
                'code': status.HTTP_403_FORBIDDEN,
                'msg': 'user is banned',
                'data': None,
            }
        
        # create the session
        user_auth_info = {
            'user_id': user_logging_in['id'],
            'username': user_logging_in['username'],
            'role': user_logging_in['role'],
        }
        SessionManager.create_session(request, user_auth_info)

        # log and return
        message = f"User {user_auth_info['username']} (id: {user_auth_info['user_id']}) logged in"
        background_tasks.add_task(logs.write_user_management_log, message)
        return {
            'code': status.HTTP_200_OK,
            'msg': 'login success',
            'data': user_auth_info,
        }
    
@router.post('/logout')
async def user_logoff(request: Request, response: Response, background_tasks: BackgroundTasks):

    """log out the user posting the request"""

    current_user = SessionManager.get_current_user(request)
    if not current_user:
        # the user is not logged in
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'code': status.HTTP_401_UNAUTHORIZED,
            'msg': 'user has not logged in',
        }
    
    # log the logging off
    message = f"User {current_user['username']} (id: {current_user['user_id']}) logged off"
    background_tasks.add_task(logs.write_user_management_log, message)
    #delete the session
    SessionManager.delete_session(request)
    return {
        'code': status.HTTP_200_OK,
        'msg': 'logout success',
        'data': None,
    }
