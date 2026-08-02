import asyncio
import logging

from pydantic import TypeAdapter

from dispatcher.core import cache_manager, settings
from dispatcher.schemas.bookmark import LinkdingBookmark
from dispatcher.schemas.preference import UserPreference
from dispatcher.schemas.user import AuthUser
from dispatcher.services.bookmark_service import BookmarkService
from dispatcher.services.linkding_service import LinkdingService
from dispatcher.services.session_service import UserSessionService
from dispatcher.services.user_service import UserService

logger = logging.getLogger(__name__)


async def _reset_tags(user: AuthUser, tags: list[str]):
    adapter = TypeAdapter(list[str])
    bookark_service = BookmarkService(user)

    all_tags = await bookark_service.get_db_tags()
    bundles_set = await bookark_service.get_bundles_set()

    await cache_manager.set_binary(
        f"tags:all:{user.id}",
        adapter.dump_json(list(set(all_tags + tags) - bundles_set)),
    )


async def process_bookmark_save(ctx: dict, token: str, payload: dict):
    try:
        user = await UserService.get_user(token)

        if user:
            linkding_service = LinkdingService(user.token, settings.linkding)
            session_service = UserSessionService(user)

            user_preference = UserPreference.model_validate(payload)
            bookmark = LinkdingBookmark.model_validate(payload)

            if user_preference.bundle:
                bookmark.tags += [user_preference.bundle]

            bookmark = await linkding_service.save_bookmark(bookmark)

            if bookmark:
                async with asyncio.TaskGroup() as tg:
                    preference_task = tg.create_task(
                        session_service.set(user_preference)
                    )

                    tags_result = await _reset_tags(user, bookmark.tags)

                preference_result = preference_task.result()

                if not preference_result:
                    logger.warning("User selection is not saved in cache.")

                if not tags_result:
                    logger.warning("Tags selection is not saved in cache.")
            else:
                logger.warning("Bookmark is not saved.")
        else:
            logger.warning("User is not found.")
    except Exception as ex:
        logger.error(f"Saving bookmark failed. {ex}")
        raise ex
