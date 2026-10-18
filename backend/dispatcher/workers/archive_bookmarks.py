import logging
import os
from datetime import UTC, datetime, timedelta
from urllib.parse import urlparse

import cloudscraper
import httpx
from cloudscraper import CloudScraper
from requests import RequestException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncScalarResult, AsyncSession

from dispatcher.db import async_session_factory
from dispatcher.db.models import LinkdingDBBookmark
from dispatcher.services.user_service import UserService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

ARCHIVE_BOOKMARK_USERS = os.getenv("LINKDING_ARCHIVE_BOOKMARK_USERS", "[]").split(",")
ARCHIVE_BOOKMARK_DAYS_AFTER = 1


async def _get_bookmarks(
    session: AsyncSession, user_id: int
) -> AsyncScalarResult[LinkdingDBBookmark]:
    query = (
        select(LinkdingDBBookmark)
        .filter(LinkdingDBBookmark.owner_id == user_id)
        .filter(~LinkdingDBBookmark.is_archived)
        .filter(
            LinkdingDBBookmark.date_modified
            <= datetime.now(UTC) - timedelta(days=ARCHIVE_BOOKMARK_DAYS_AFTER)
        )
    )

    return await session.stream_scalars(query.execution_options(yield_per=100))


def _get_headers(url: str) -> dict[str, str]:
    parsed_url = urlparse(url)
    origin = (
        f"{parsed_url.scheme}://{parsed_url.netloc}"
        if parsed_url.scheme and parsed_url.netloc
        else ""
    )

    return {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,image/svg+xml,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": origin,
        "Sec-Fetch-Site": "cross-site" if parsed_url.netloc else "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not.A/Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
    }


async def _process_bookmark(
    session: AsyncSession, scraper: CloudScraper, bookmark: LinkdingDBBookmark
):
    headers = _get_headers(bookmark.url)
    response = scraper.get(bookmark.url, headers=headers, allow_redirects=True)

    if response.status_code in (404, 410):
        modified_at = datetime.now(UTC)
        await session.execute(
            update(LinkdingDBBookmark)
            .where(LinkdingDBBookmark.id == bookmark.id)
            .values(is_archived=True, date_modified=modified_at)
        )
        await session.commit()
        bookmark.is_archived = True
        bookmark.date_modified = modified_at
        logger.info(
            "Archived unavailable bookmark %s with status %s",
            bookmark.id,
            response.status_code,
        )
        return

    response.raise_for_status()


async def process_bookmark_archive(ctx: dict) -> bool:
    scraper = cloudscraper.create_scraper()

    for token in ARCHIVE_BOOKMARK_USERS:
        user = await UserService.get_user(token)

        if not user:
            logger.warning("User not found")
            return False

        async with async_session_factory() as session:
            bookmarks = await _get_bookmarks(session, user.id)

            async for bookmark in bookmarks:
                if not bookmark.preview_image_file:
                    try:
                        await _process_bookmark(session, scraper, bookmark)
                    except (httpx.HTTPError, RequestException) as exc:
                        logger.warning(
                            "Failed fetching bookmark Info "
                            f"{bookmark.id}:{bookmark.url}\n{exc}"
                        )
                    except Exception as ex:
                        logger.warning(
                            f"Failed updating bookmark: {bookmark.id}:\n{ex}"
                        )

    return True
