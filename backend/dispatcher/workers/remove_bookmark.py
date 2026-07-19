import logging

from dispatcher.core import settings
from dispatcher.services.linkding_service import LinkdingService
from dispatcher.services.user_service import UserService

logger = logging.getLogger(__name__)


async def process_bookmark_remove(ctx: dict, token: str, bookmark_id: int | None):
    try:
        user = await UserService.get_user(token)

        if user and bookmark_id:
            linkding_service = LinkdingService(user.token, settings.linkding)

            success = await linkding_service.remove_bookmark(bookmark_id)

            if not success:
                logger.warning("Bookmark removing unsuccessful.")
        else:
            logger.warning("User or bookmark id not found.")

    except Exception as ex:
        logger.error(f"Removing bookmark failed. {ex}")
