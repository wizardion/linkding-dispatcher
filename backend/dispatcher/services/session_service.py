import logging

from pydantic import TypeAdapter

from dispatcher.core import cache_manager
from dispatcher.schemas import AuthUser, UserPreference

logger = logging.getLogger(__name__)


class UserSessionService:
    def __init__(self, user: AuthUser):
        self.user = user
        pass

    async def get(self) -> UserPreference | None:
        try:
            adapter = TypeAdapter(UserPreference)
            data = await cache_manager.get_binary(f"user-session:set:{self.user.id}")

            if data:
                return adapter.validate_json(data)
        except Exception as ex:
            logger.error(f"Error getting session. {ex}")

        return UserPreference()

    async def set(self, user_session: UserPreference) -> UserPreference | None:
        try:
            adapter = TypeAdapter(UserPreference)
            data = adapter.dump_json(user_session)

            await cache_manager.set_binary(f"user-session:set:{self.user.id}", data)

            return user_session
        except Exception as ex:
            logger.error(f"Error setting session. {ex}")

        return None
