import re
from operator import attrgetter

from pydantic import TypeAdapter
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from dispatcher.core import db_cache
from dispatcher.core.settings import CacheStrategy
from dispatcher.db import (
    LinkdingDBBookmark,
    LinkdingDBBookmarkTag,
    LinkdingDBBundle,
    LinkdingDBTag,
    async_session_factory,
)
from dispatcher.schemas import AuthUser, Bundle
from dispatcher.schemas.bookmark import Bookmark


class BookmarkService:
    def __init__(self, user: AuthUser):
        self.user = user

    @db_cache(lambda cls, _: f"bundles:set:{attrgetter('user.id')(cls)}")
    async def _get_bundles_set(self, session: AsyncSession) -> set[str]:
        query = (
            select(LinkdingDBBundle.all_tags)
            .filter(LinkdingDBBundle.owner_id == self.user.id)
            .order_by(LinkdingDBBundle.order)
        )
        bundles = (await session.scalars(query)).all()

        return {i for b in bundles for i in re.split(r"[,\s]+", b)}

    async def get_bundles_set(self) -> set[str]:
        async with async_session_factory() as session:
            bundles_set = await self._get_bundles_set(session)

        return bundles_set

    async def check_bookmark(self, url: str) -> Bookmark | None:
        if not url:
            return None

        variants = [url, url.rstrip("/") if url.endswith("/") else url + "/"]

        async with async_session_factory() as session:
            query = (
                select(LinkdingDBBookmark)
                .filter(LinkdingDBBookmark.owner_id == self.user.id)
                .where(LinkdingDBBookmark.url.in_(variants))
            )
            db_bookmark = await session.scalar(query)

            if db_bookmark:
                bundles = await self._get_bundles_set(session)
                tags_query = (
                    select(LinkdingDBTag.name)
                    .filter(LinkdingDBTag.owner_id == self.user.id)
                    .where(
                        exists(
                            select(1).where(
                                (LinkdingDBBookmarkTag.bookmark_id == db_bookmark.id)
                                & (LinkdingDBBookmarkTag.tag_id == LinkdingDBTag.id)
                            )
                        )
                    )
                )

                bookmark_tags = set((await session.scalars(tags_query)).all())

                return Bookmark(
                    id=db_bookmark.id,
                    url=db_bookmark.url,
                    title=db_bookmark.title,
                    tag_names=list(bookmark_tags - bundles),
                    bundle=" ".join(bookmark_tags & bundles),
                    is_archived=db_bookmark.is_archived,
                    description=db_bookmark.description,
                )

        return None

    @db_cache(
        lambda cls: f"bundles:all:{attrgetter('user.id')(cls)}",
        CacheStrategy.ONE_MONTH,
    )
    async def get_bundles(self) -> list[Bundle]:
        adapter = TypeAdapter(list[Bundle])

        async with async_session_factory() as session:
            query = (
                select(LinkdingDBBundle)
                .filter(LinkdingDBBundle.owner_id == self.user.id)
                .order_by(LinkdingDBBundle.order)
            )
            bundles = (await session.scalars(query)).all()

        return adapter.validate_python(bundles)

    @db_cache(
        lambda cls: f"tags:all:{attrgetter('user.id')(cls)}",
        CacheStrategy.ONE_WEEK,
    )
    async def get_tags(self) -> list[str]:
        return await self.get_db_tags()

    async def get_db_tags(self) -> list[str]:
        async with async_session_factory() as session:
            bundles_set = await self._get_bundles_set(session)
            all_tags_query = (
                select(LinkdingDBTag.name)
                .filter(LinkdingDBTag.owner_id == self.user.id)
                .where(~LinkdingDBTag.name.in_(bundles_set))
                .order_by(LinkdingDBTag.name)
            )

            active_tags_result = await session.execute(all_tags_query)
            active_tags = active_tags_result.scalars().all()

        return list(active_tags)
