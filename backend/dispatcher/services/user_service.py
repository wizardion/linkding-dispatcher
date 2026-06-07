import logging

from sqlalchemy import select

from dispatcher.core import CacheStrategy, db_cache
from dispatcher.db import (
    async_session_factory,
)
from dispatcher.db.models import LinkdingDBApiToken, LinkdingDBUser
from dispatcher.schemas import AuthUser

logger = logging.getLogger(__name__)


class UserService:
    @classmethod
    @db_cache(lambda _, token: f"user:token:{token}", CacheStrategy.ONE_MONTH)
    async def get_user(cls, token: str) -> AuthUser | None:
        try:
            async with async_session_factory() as session:
                query = (
                    select(
                        LinkdingDBUser.id,
                        LinkdingDBUser.username,
                        LinkdingDBUser.first_name,
                        LinkdingDBUser.last_name,
                        LinkdingDBUser.email,
                        LinkdingDBApiToken.key.label("token"),
                    )
                    .join(
                        LinkdingDBApiToken,
                        LinkdingDBApiToken.user_id == LinkdingDBUser.id,
                    )
                    .where(LinkdingDBApiToken.key == token)
                )
                db_user = (await session.execute(query)).one()

            return AuthUser.model_validate(db_user)
        except Exception as ex:
            logger.error(f"Error getting user info. {ex}")

        return None
