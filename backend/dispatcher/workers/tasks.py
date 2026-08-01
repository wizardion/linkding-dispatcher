import logging
import re
import time

from sqlalchemy import delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from dispatcher.core import settings
from dispatcher.db import (
    LinkdingDBBookmark,
    async_session_factory,
)
from dispatcher.db.models import LinkdingDBBookmarkTag, LinkdingDBBundle, LinkdingDBTag
from dispatcher.schemas.bookmark import LinkdingBookmark
from dispatcher.services.linkding_service import LinkdingService
from dispatcher.services.user_service import UserService

logger = logging.getLogger(__name__)


class MigratingException(Exception):
    def __init__(self, message: str, id: int, *args: object) -> None:
        super().__init__(message, id, *args)
        self.message = message
        self.id = id


async def _get_bundles_set(session: AsyncSession, user_id: int) -> set[str]:
    query = (
        select(LinkdingDBBundle.all_tags)
        .filter(LinkdingDBBundle.owner_id == user_id)
        .order_by(LinkdingDBBundle.order)
    )
    bundles = (await session.scalars(query)).all()

    return {i for b in bundles for i in re.split(r"[,\s]+", b)}


async def _check_bookmark(
    session: AsyncSession, variants: list[str], user_id: int
) -> bool | None:
    query = select(
        exists().where(
            (LinkdingDBBookmark.url.in_(variants))
            & (LinkdingDBBookmark.owner_id == user_id)
        )
    )

    is_exist = await session.scalar(query)

    return is_exist


async def _get_bookmark_tags(session: AsyncSession, bookmark_id: int, user_id: int):
    tags_query = (
        select(LinkdingDBTag.name)
        .filter(LinkdingDBTag.owner_id == user_id)
        .where(
            exists(
                select(1).where(
                    (LinkdingDBBookmarkTag.bookmark_id == bookmark_id)
                    & (LinkdingDBBookmarkTag.tag_id == LinkdingDBTag.id)
                )
            )
        )
    )

    return set((await session.scalars(tags_query)).all())


async def _get_bookmarks(
    session: AsyncSession, user_id: int, batch_size: int, exclude: list[int]
) -> list[LinkdingDBBookmark]:
    query = (
        select(LinkdingDBBookmark)
        .filter(LinkdingDBBookmark.owner_id == user_id)
        .filter(LinkdingDBBookmark.is_archived)
        .filter(~LinkdingDBBookmark.id.in_(exclude))
        .limit(batch_size)
    )

    db_bookmark_result = await session.execute(query)
    db_bookmarks = db_bookmark_result.scalars().all()

    return list(db_bookmarks)


async def _remove_abandoned_tags(session: AsyncSession, user_id: int):
    tags_query = (
        delete(LinkdingDBTag)
        .filter(LinkdingDBTag.owner_id == user_id)
        .where(
            ~exists(select(1).where(LinkdingDBBookmarkTag.tag_id == LinkdingDBTag.id))
        )
    )

    await session.execute(tags_query)
    await session.commit()


async def process_bookmark_migrate(ctx: dict, token: str) -> bool:
    BATCH_SIZE = 200
    NEW_USER_TOKEN = "..."

    try:
        user = await UserService.get_user(token)
        archived_user = await UserService.get_user(NEW_USER_TOKEN)

        if not user or not archived_user:
            raise Exception("User is not defined.")

        linkding_service = LinkdingService(user.token, settings.linkding)
        archived_service = LinkdingService(archived_user.token, settings.linkding)
        failed_bookmarks: list[int] = []

        async with async_session_factory() as session:
            bundles_set = await _get_bundles_set(session, user.id)
            bookmarks = await _get_bookmarks(
                session, user.id, BATCH_SIZE, failed_bookmarks
            )

        print("--migrating--")
        print("user", user.id)
        print("archived_user", archived_user.id)
        print("bookmarks enqueued:", len(bookmarks))

        while bookmarks:
            async with async_session_factory() as session:
                for db_bookmark in bookmarks:
                    try:
                        removed = False
                        is_exists = await _check_bookmark(
                            session,
                            [db_bookmark.url, db_bookmark.url_normalized],
                            archived_user.id,
                        )

                        if is_exists:
                            failed_bookmarks.append(db_bookmark.id)
                            logger.warning(f"Bookmark exists: {db_bookmark.id}")
                            continue

                        bookmark_tags = await _get_bookmark_tags(
                            session, db_bookmark.id, user.id
                        )

                        payload = LinkdingBookmark(
                            url=db_bookmark.url,
                            title=db_bookmark.title,
                            tag_names=list(bookmark_tags - bundles_set),
                            is_archived=False,
                            description=db_bookmark.description,
                        )

                        print("--payload--")
                        print(payload.model_dump_json())
                        print("")

                        bookmark = await archived_service.save_bookmark(payload)

                        if bookmark:
                            removed = await linkding_service.remove_bookmark(
                                db_bookmark.id
                            )

                            if not removed:
                                raise MigratingException(
                                    f"Error removing the bookmark {db_bookmark.id}",
                                    db_bookmark.id,
                                )

                        if not bookmark or not removed:
                            raise MigratingException(
                                f"Error migrating the bookmark {db_bookmark.id}",
                                db_bookmark.id,
                            )

                        time.sleep(5)
                    except MigratingException as e:
                        logger.error(e.message)
                        failed_bookmarks.append(e.id)

                        if len(failed_bookmarks) > 9:
                            raise Exception(
                                "Cannot proceed with failed more then 10."
                            ) from e
                    except Exception as e:
                        logger.error(
                            f"Unexpected error occured during migrating bookmark. {e}"
                        )
                        raise e

                print("---------------------------------------------------------------")
                print("The Batch process finished migrating bookmarks:", len(bookmarks))

                bookmarks = await _get_bookmarks(
                    session, user.id, BATCH_SIZE, failed_bookmarks
                )

                if bookmarks:
                    print("bookmarks enqueued:", len(bookmarks))
                print("")

        print("---------------------------------------------------------------")
        print("Removing abandoned tags ...")

        time.sleep(20)

        async with async_session_factory() as session:
            await _remove_abandoned_tags(session, user.id)

        if failed_bookmarks:
            print("Several bookmarks failed to migrate:")

            for id in failed_bookmarks:
                print(f"- failed bookmark: {id}")

            print("")

            return False

        print("Migration is done!")
        print("")

        return True
    except Exception as ex:
        logger.error(f"Failed migrating bookmarks. {ex}")

    return False
