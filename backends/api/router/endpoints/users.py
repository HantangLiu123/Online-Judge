from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi_cache.decorator import cache
from api.core.security import auth
from api.utils import user_tool
from shared.schemas import UserCredentials, Role
from shared.db import user_db
from shared.models import User, UserRole
from shared.utils import oj_cache

router = APIRouter(prefix='/users')

@router.post('/')
async def user_sign_in(user_credentials: UserCredentials):

    """signing in the new user"""

    new_user = await user_tool.convert_user_info(user_credentials, 'user')
    user_id = await user_db.create_user_in_db(new_user)
    if user_id is None:
        # the username already exists
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                'code': status.HTTP_400_BAD_REQUEST,
                'msg': 'the username already exists',
                'data': None,
            }
        )
    
    return {
        'code': status.HTTP_200_OK,
        'msg': 'register success',
        'data': {'user_id': user_id},
    }

@router.post('/admin')
async def create_admin(
    admin_credentials: UserCredentials,
    current_user: User = Depends(auth.get_current_user_factory(True)),
):
    
    """signing in new admin, only an admin can do this"""

    # create the new admin
    new_admin = await user_tool.convert_user_info(admin_credentials, 'admin')
    admin_id = await user_db.create_user_in_db(new_admin)
    if admin_id is None:
        # the username already exists
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                'code': status.HTTP_400_BAD_REQUEST,
                'msg': 'the username already exists',
                'data': None,
            }
        )
    
    return {
        'code': status.HTTP_200_OK,
        'msg': 'success',
        'data': {
            'user_id': admin_id,
            'username': new_admin.username,
        }
    }

@router.get('/{user_id}')
async def get_user_info(
    user_id: int,
    current_user: User = Depends(auth.get_current_user_factory(False))
):

    """get the user's info according to the id
    
    This endpoint returns the user info according to the user id, 
    only an admin can check other users' info. In this function, 
    the get_current_user_factory is set to false since the user 
    should be able to get his/her own info.
    """

    if user_id == current_user.id:
        return {
            'code': status.HTTP_200_OK,
            'msg': 'success',
            'data': {
                'user_id': current_user.id,
                'username': current_user.username,
                'join_time': current_user.join_time.isoformat(),
                'role': current_user.role,
                'submit_count': current_user.submit_count,
                'resolve_count': current_user.resolve_count,
            }
        }
    
    if current_user.role != UserRole.ADMIN:
        # the user has no authority
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                'code': status.HTTP_403_FORBIDDEN,
                'msg': 'the user is forbiddened',
                'data': None,
            }
        )
    
    # get the user
    user = await user_db.get_user_by_id(user_id)
    if user is None:
        # cannot find the user
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'code': status.HTTP_404_NOT_FOUND,
                'msg': 'there is no such user',
                'data': None,
            }
        )
    
    return {
        'code': status.HTTP_200_OK,
        'msg': 'success',
        'data': {
            'user_id': user.id,
            'username': user.username,
            'join_time': user.join_time.isoformat(),
            'role': user.role,
            'submit_count': user.submit_count,
            'resolve_count': user.resolve_count,
        }
    }

@router.put('/{user_id}/role')
async def change_user_role(
    user_id: int,
    new_role: Role, 
    current_user: User = Depends(auth.get_current_user_factory(True)),
):
    
    """change the role of a user, only an admin is allowed"""
    
    # get the user to change the role
    user = await user_db.get_user_by_id(user_id)
    if user is None:
        # cannot find the user
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'code': status.HTTP_404_NOT_FOUND,
                'msg': 'there is no such user',
                'data': None,
            }
        )
    
    # change the role
    await user_db.change_user_role(user, UserRole(new_role.role))
    return {
        'code': status.HTTP_200_OK,
        'msg': 'role updates',
        'data': {
            'user_id': user_id,
            'role': new_role.role,
        }
    }

@router.get('/')
@cache(
    expire=120,
    key_builder=oj_cache.user_list_key_builder,
)
async def get_user_list(
    current_user: User = Depends(auth.get_current_user_factory(True)),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
):
    
    """returns the user list, only an admin can do this"""
    
    # get the list
    total, total_page, users = await user_tool.user_list_paginated(current_user, page, page_size)
    return {
        'code': status.HTTP_200_OK,
        'msg': 'success',
        'data': {
            'total': total,
            'total_page': total_page,
            'users': users,
        }
    }
