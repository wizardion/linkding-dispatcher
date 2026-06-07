import logging

from fastapi import status
from starlette.authentication import AuthCredentials, AuthenticationBackend
from starlette.exceptions import HTTPException
from starlette.requests import HTTPConnection

from dispatcher.services.user_service import UserService

logger = logging.getLogger(__name__)


# 1. Define your custom auth mechanism
class JWTAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn: HTTPConnection):
        api_key = conn.headers["X-API-Key"]

        if not api_key or len(api_key) != 40:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid API Key provided.")

        try:
            user = await UserService.get_user(api_key)

            if not user:
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN, "Invalid API Key provided."
                )

            return AuthCredentials(["authenticated"]), user
        except Exception as ex:
            logger.error(f"Authentication error occured. {ex}")
            raise ex
