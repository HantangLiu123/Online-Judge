from ..models import User
from ..schemas import UserData

def user_data_to_user(data: UserData) -> User:

    """parse userdata to user"""

    data_dict = data.model_dump()
    return User(**data_dict)

def user_to_user_data(user: User) -> UserData:

    """parse user to userdata"""

    return UserData(
        id=user.id,
        username=user.username,
        password=user.password,
        role=str(user.role), # pyright: ignore[reportArgumentType]
        join_time=user.join_time,
        submit_count=user.submit_count,
        resolve_count=user.resolve_count,
    )
