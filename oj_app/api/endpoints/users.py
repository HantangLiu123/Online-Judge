from fastapi import status, Response, APIRouter, Request, BackgroundTasks, Query
from fastapi_cache.decorator import cache
from pydantic import ValidationError
from oj_app.models.schemas import User, NewRole
from oj_app.core.security.UserManager import userManager
from oj_app.core.security.CacheManager import cacheManager
from oj_app.core.security.SessionManager import AuthenticationError
from oj_app.dependencies import common
from oj_app.core.config import logs

router = APIRouter(prefix='/users')

@router.post('/')
async def user_sign_in(response: Response, user: dict, background_tasks: BackgroundTasks) -> dict:

    """signing in the new user"""

    try:
        new_user = User(**user)
    except ValidationError:
        # can't parse the input to User, format is wrong
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'code': status.HTTP_400_BAD_REQUEST,
            'msg': 'wrong parameters',
            'data': None,
        }
    
    try:
        id = await userManager.create_user(new_user)
    except ValueError:
        # the username is already existed
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'code': status.HTTP_400_BAD_REQUEST,
            'msg': 'the username is already existed',
            'data': None,
        }
    
    if id is None:
        # the user id should not be None at this point
        raise common.UnexpectedError
    
    # log and return
    message = f"User created. Username: {new_user.username}. User_id: {id}."
    background_tasks.add_task(logs.write_user_management_log, message)
    return {
        'code': status.HTTP_200_OK,
        'msg': 'register success',
        'data': {'user_id': id},
    }
        
@router.post('/admin')
async def create_admin(request: Request, response: Response, user: dict, background_tasks: BackgroundTasks) -> dict:

    """create an admin user, only another admin can do this"""

    try:
        # get info of the current user
        current_user = common.get_current_user(request)
        if current_user['role'] != 'admin':
            # the user has no authority
            response.status_code = status.HTTP_403_FORBIDDEN
            return {
                'code': status.HTTP_403_FORBIDDEN,
                'msg': 'user has no authority',
                'data': None,
            }
        
        # parse the admin to User type
        new_admin = User(**user)
        new_admin.role = 'admin'
        
        # create the new admin
        new_id = await userManager.create_user(new_admin)
    except AuthenticationError:
        # the user is not logged in
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'code': status.HTTP_401_UNAUTHORIZED,
            'msg': 'user has not logged in',
            'data': None,
        }
    except ValidationError:
        # can't parse the input to User, format is wrong
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'code': status.HTTP_400_BAD_REQUEST,
            'msg': 'wrong parameters',
            'data': None,
        }
    except ValueError:
        # the username is already existed
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'code': status.HTTP_400_BAD_REQUEST,
            'msg': 'the username is already existed',
            'data': None,
        }
    else:
        # log and create
        message = f"Admin user created by {current_user['username']} (id: {current_user['user_id']}). Username: {new_admin.username}. User_id: {new_id}."
        background_tasks.add_task(logs.write_user_management_log, message)
        return {
            'code': status.HTTP_200_OK,
            'msg': 'success',
            'data': {
                'user_id': new_id,
                'username': new_admin.username,
            }
        }

@router.get('/{user_id}')
async def get_user_info(request: Request, response: Response, user_id: int) -> dict:
    
    """get the user's info by his/her id"""

    try:
        current_user = common.get_current_user(request)
    except AuthenticationError:
        # the user is not logged in
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'code': status.HTTP_401_UNAUTHORIZED,
            'msg': 'user has not logged in',
            'data': None,
        }
    else:
        if current_user['user_id'] == user_id:
            # the user is checking himself/herself
            return {
                'code': status.HTTP_200_OK,
                'msg': 'success',
                'data': current_user,
            }
        
        if current_user['role'] != 'admin':
            # the user has no authority
            response.status_code = status.HTTP_403_FORBIDDEN
            return {
                'code': status.HTTP_403_FORBIDDEN,
                'msg': 'user has no authority',
                'data': None,
            }
        
        # the user is not checking himself/herself, but he/she is an admin
        target_user = await userManager.get_user_by_id(user_id)
        if not target_user:
            # can't find the user
            response.status_code = status.HTTP_404_NOT_FOUND
            return {
                'code': status.HTTP_404_NOT_FOUND,
                'msg': 'the user does not exist',
                'data': None,
            }
        else:
            return {
                'code': status.HTTP_200_OK,
                'msg': 'success',
                'data': {
                    'user_id': target_user['id'],
                    'username': target_user['username'],
                    'role': target_user['role'],
                },
            }
        
@router.put('/{user_id}/role')
async def change_role_of_user(
        request: Request,
        response: Response,
        user_id: int,
        new_role: NewRole,
        background_tasks: BackgroundTasks
    ) -> dict:

    """change the user to his/her new role, only admin can do this"""

    # get current user
    try:
        current_user = common.get_current_user(request)
    except AuthenticationError:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'code': status.HTTP_401_UNAUTHORIZED,
            'msg': 'user not logged in',
            'data': None,
        }
    else:
        if current_user['role'] != 'admin':
            # the user is not an admin
            response.status_code = status.HTTP_403_FORBIDDEN
            return {
                'code': status.HTTP_403_FORBIDDEN,
                'msg': 'user has no authority',
                'data': None,
            }
        else:
            changed_id, changed_role = await userManager.change_user_role(user_id, new_role.role)

            # log and return
            message = f"User {changed_id}'s role is changed by admin {current_user['username']} (id: {current_user['user_id']}). The role is change to {changed_role}."
            background_tasks.add_task(logs.write_user_management_log, message)
            return {
                'code': status.HTTP_200_OK,
                'msg': 'role updated',
                'data': {
                    'user_id': changed_id,
                    'role': changed_role,
                },
            }
        
@router.get('/')
@cache(
    expire=120,
    key_builder=cacheManager.task_funcs_map['user_list'].key_builder,
) # cache for 2 minutes
async def get_user_list(
        request: Request,
        response: Response,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1),
    ):

    """get the user list, only an admin can do this
    
    This function returns the user list according to the parameters. The page_size
    should be 10, 20, 50, or 100, and its default is 20.
    """

    # get current user
    try:
        current_user = common.get_current_user(request)
    except AuthenticationError:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'code': status.HTTP_401_UNAUTHORIZED,
            'msg': 'user not logged in',
            'data': None,
        }
    
    if current_user['role'] != 'admin':
        # the user is not an admin
        response.status_code = status.HTTP_403_FORBIDDEN
        return {
            'code': status.HTTP_403_FORBIDDEN,
            'msg': 'user has no authority',
            'data': None,
        }
    
    if page_size != 10 and page_size != 20 and page_size != 50 and page_size != 100:
        # bad request
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'code': status.HTTP_400_BAD_REQUEST,
            'msg': 'the page size is not supported',
            'data': None,
        }
    
    try:
        total, user_list = await userManager.get_users(page, page_size)
    except ValueError:
        # the page is too large
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'code': status.HTTP_404_NOT_FOUND,
            'msg': 'the page exceeds the maximum page number',
            'data': None,
        }
    
    return {
        'code': status.HTTP_200_OK,
        'msg': 'success',
        'data': {
            'total': total,
            'users': user_list,
        },
    }
