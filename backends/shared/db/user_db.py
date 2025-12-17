import logging
from tortoise.exceptions import IntegrityError
from ..models import User, UserRole
from ..schemas import UserToCreate
from ..utils import oj_cache

logger = logging.getLogger('debug')

async def get_user_by_id(user_id: int):

    """find the user by his/her id"""

    return await User.get_or_none(pk=user_id)

async def get_user_by_username(username: str):

    """find the user by his/her username"""

    return await User.get_or_none(username=username)

async def create_user_in_db(user_to_create: UserToCreate) -> int | None:

    """create a user according to the model.
    
    This function returns the user id if the process succeeds,
    returns None if it fails
    """

    try:
        user = await User.create(
            username=user_to_create.username,
            password=user_to_create.hashed_password,
            role=user_to_create.role,
        )
    except IntegrityError:
        logger.debug('failed to create new user')
        return None
    
    # remove the corresponding cache
    last_user = await User.filter(id__lt=user.id).order_by('-id').first()
    if last_user is not None:
        await oj_cache.delete_cache(item_type='user', user_id=last_user.id)
    return user.id

async def change_user_role(user: User, role: UserRole):

    """update the role of the corresponding user"""

    user.role = role
    await user.save()
    await oj_cache.delete_cache(item_type='user', user_id=user.id)

async def delete_user_in_db(user: User):

    """delete the corresponding user"""

    await oj_cache.delete_cache(item_type='user', user_id=user.id)
    await user.delete()
    

async def add_submit_count(user: User):

    """adding the user's submit count"""

    user.submit_count += 1
    await user.save()
    await oj_cache.delete_cache(item_type='user', user_id=user.id)

async def add_resolve_count(user: User):

    """adding the user's resolve count"""

    user.resolve_count += 1
    await user.save()
    await oj_cache.delete_cache(item_type='user', user_id=user.id)

async def reset_user_table():

    """reset the table"""

    await User.all().delete()

async def export_user_table():

    """export all users"""

    return await User.all().order_by('id')

async def import_user_in_db(users: list[User]):

    """import all users"""

    await User.bulk_create(users, ignore_conflicts=True)
