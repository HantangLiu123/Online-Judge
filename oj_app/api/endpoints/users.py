from fastapi import status, Response, APIRouter, Request, BackgroundTasks, Query
from pydantic import ValidationError
from oj_app.models.schemas import User, NewRole
from oj_app.core.security.UserManager import userManager
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
    else:
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
        else:
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
        new_admin = User(**user)
        new_admin.role = 'admin'
    except ValidationError:
        # can't parse the input to User, format is wrong
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'code': status.HTTP_400_BAD_REQUEST,
            'msg': 'wrong parameters',
            'data': None,
        }
    else:
        # check if the current user is an admin
        try:
            current_user = common.get_current_user(request)
        except AuthenticationError:
            # the user is not logged in
            response.status_code = status.HTTP_403_FORBIDDEN
            return {
                'code': status.HTTP_403_FORBIDDEN,
                'msg': 'user has not logged in',
                'data': None,
            }
        else:
            if current_user['role'] != 'admin':
                # the user has no authority
                response.status_code = status.HTTP_403_FORBIDDEN
                return {
                    'code': status.HTTP_403_FORBIDDEN,
                    'msg': 'user has no authority',
                    'data': None,
                }
            
            # create the new admin
            try:
                new_id = await userManager.create_user(new_admin)
            except ValueError:
                # the username is already existed
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {
                    'code': status.HTTP_400_BAD_REQUEST,
                    'msg': 'the username is already existed',
                    'data': None,
                }
            else:
                if new_id is None:
                    # facing somg unexpected error
                    raise common.UnexpectedError
                
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
        response.status_code = status.HTTP_403_FORBIDDEN
        return {
            'code': status.HTTP_403_FORBIDDEN,
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
        response.status_code = status.HTTP_403_FORBIDDEN
        return {
            'code': status.HTTP_403_FORBIDDEN,
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
async def get_user_list(
        request: Request,
        response: Response,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1),
    ):

    """get the user list, only an admin can do this"""

    # get current user
    try:
        current_user = common.get_current_user(request)
    except AuthenticationError:
        response.status_code = status.HTTP_403_FORBIDDEN
        return {
            'code': status.HTTP_403_FORBIDDEN,
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
            # get the list
            user_list = await userManager.get_all_users()
            
            # check if the page number is larger than maximum page
            max_page_num = len(user_list) // page_size + 1
            if page > max_page_num:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {
                    'code': status.HTTP_404_NOT_FOUND,
                    'msg': 'the page number exceeds the max page number',
                    'data': None,
                }
            
            # return the list segment

            return_list = user_list[page_size * (page - 1):page_size * page]
            return {
                'code': status.HTTP_200_OK,
                'msg': 'success',
                'data': {
                    'total': len(return_list),
                    'users': return_list,
                },
            }
