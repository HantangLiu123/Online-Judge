from datetime import datetime
from fastapi import Response, APIRouter, status, Depends, HTTPException
from shared.schemas import UserCredentials
from shared.models import User, UserRole
from api.core.security import auth
from api.core.config import settings

router = APIRouter(prefix='/auth')

@router.post('/login')
async def user_login(
    response: Response,
    login_info: UserCredentials,
    current_user: User | None = Depends(auth.get_current_user_login),
):

    """login the user if the credentials can be verified
    
    This endpoint log the user in if the credentials are varied. However, if the user
    is already logged in, it will return http ok directly.
    """

    if current_user is not None:
        return {
            'code': status.HTTP_200_OK,
            'msg': 'the user has already logged in',
            'data': {
                'user_id': current_user.id,
                'username': current_user.username,
                'role': current_user.role,
            }
        }
    
    # get the user logged in
    user = await auth.authenticate_user(login_info)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                'code': status.HTTP_401_UNAUTHORIZED,
                'msg': 'the username or password is incorrect',
                'data': None,
            }
        )
    
    # user banned cannot log in
    if user.role == UserRole.BANNED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                'code': status.HTTP_403_FORBIDDEN,
                'msg': 'the user is banned',
                'data': None,
            }
        )
    
    # create the token
    access_token = auth.create_access_token(
        data={
            'sub': user.username,
            'role': user.role,
            'time': datetime.now().isoformat(),
        }
    )
    response.set_cookie(
        key=auth.COOKIE_NAME,
        value=access_token,
        httponly=settings.token_http_only,
        secure=True,
        samesite=settings.same_site, # type: ignore
        max_age=settings.token_max_age,
    )

    return {
        'code': status.HTTP_200_OK,
        'msg': 'login success',
        'data': {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
        }
    }

@router.post('/logout')
async def logout_user(response: Response, current_user: User = Depends(auth.get_current_user)):

    """log out the user if the user is logged in"""

    response.delete_cookie(auth.COOKIE_NAME)
    return {
        'code': status.HTTP_200_OK,
        'msg': 'logout success',
        'data': None,
    }
