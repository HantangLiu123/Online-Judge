import logging
from fastapi import Request
from fastapi.responses import Response
from .security import auth

logger = logging.getLogger("user_access")

async def log_middleware(request: Request, call_next):

    """middleware for user access log (from chatgpt 5)"""

    user = await auth.get_current_user(request)
    if user is None:
        username = 'anonymous'
    else:
        username = user.username

    response: Response = await call_next(request)

    logger.info(
        f"{request.client.host} - {request.method} {request.url.path} " # type: ignore
        f"status={response.status_code} user={username}"
    )

    return response
