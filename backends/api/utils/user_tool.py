import bcrypt
from typing import Literal
from fastapi.concurrency import run_in_threadpool
from shared.schemas import UserCredentials, UserToCreate

async def convert_user_info(
    user_credentials: UserCredentials,
    role: Literal['user', 'admin', 'banned'],
) -> UserToCreate:

    """this function converts the user sign in info to the info needed for db"""

    hashed_password = await run_in_threadpool(
        bcrypt.hashpw,
        user_credentials.password.encode(),
        bcrypt.gensalt(),
    )

    return UserToCreate(
        username=user_credentials.username,
        hashed_password=hashed_password.decode(),
        role=role,
    )
