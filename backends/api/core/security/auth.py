from datetime import datetime, timedelta
import bcrypt
from fastapi import Request, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from jose import jwt, JWTError
from shared.schemas import UserCredentials
from shared.models import User, UserRole
from shared.db import user_db
from ..config import settings

SECRET_KEY: str = settings.secret_key # type: ignore
ALGORITHM = 'HS256'
TOKEN_MAX_AGE = settings.token_max_age
COOKIE_NAME = 'oj_token'

async def match_password(password: str, hashed_password: str) -> bool:

    """check if the password is right"""

    return await run_in_threadpool(
        bcrypt.checkpw,
        password.encode(), 
        hashed_password.encode(),
    )

async def authenticate_user(login_info: UserCredentials) -> User | None:

    """authenticate the user if the login info is verified
    
    This function returns the user in the database if the login info is verified,
    it will return None if the user does not exist or the password does not match
    """

    user = await user_db.get_user_by_username(login_info.username)
    if user is None:
        return None
    if not await match_password(login_info.password, user.password):
        return None
    return user

def create_access_token(data: dict):

    """create the token"""

    to_encode = data.copy()
    expire = datetime.now() + timedelta(seconds=TOKEN_MAX_AGE)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt

def get_current_user_factory(admin_only: bool):

    """factor the get_current_user function"""

    async def get_current_user(request: Request) -> User:

        """get the user reaching the protected endpoint"""

        credential_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                'code': status.HTTP_401_UNAUTHORIZED,
                'msg': 'the user has not logged in',
                'data': None,
            },
        )

        # get the token
        token = request.cookies.get(COOKIE_NAME)
        if token is None:
            raise credential_exception

        # check the info in the token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str | None = payload.get('sub')
            if username is None:
                # the token isn't valid
                raise credential_exception
        except JWTError:
            # there's something wrong with the token
            raise credential_exception
        
        # check if the info in the token is the same as that in the database
        user = await user_db.get_user_by_username(username)
        if user is None or user.role != payload.get('role'):
            raise credential_exception
        
        # check if the token is given before the last start up time
        token_time = datetime.fromisoformat(payload['time'])
        if token_time < request.app.state.start_up_time:
            raise credential_exception
        
        # if admin_only is true, and the user is not an admin, raise 403
        if admin_only and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    'code': status.HTTP_403_FORBIDDEN,
                    'msg': 'the user is forbiddened',
                    'data': None,
                }
            )
        return user
    
    return get_current_user

async def get_current_user_login(request: Request) -> User | None:

    """this is the get current user for the login endpoint
    
    When the user has not logged in, it will return None instead of
    raising a unauthorized code
    """

    # get the token
    token = request.cookies.get(COOKIE_NAME)
    if token is None:
        return None
    
    # check the info in the token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get('sub')
        if username is None:
            # the token isn't valid
            return None
    except JWTError:
        # there's something wrong with the token
        return None
    
    # check if the info in the token is the same as that in the database
    user = await user_db.get_user_by_username(username)
    if user is None or user.role != payload.get('role'):
        return None
    
    # check if the token is given before the last start up time
    token_time = datetime.fromisoformat(payload['time'])
    if token_time < request.app.state.start_up_time:
        return None
    return user
