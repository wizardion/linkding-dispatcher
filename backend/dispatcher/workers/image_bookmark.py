import hashlib
import io
import logging
import os
from pathlib import Path
from urllib.parse import urljoin, urlparse

import cloudscraper
import httpx
from bs4 import BeautifulSoup
from cloudscraper import CloudScraper
from PIL import Image
from requests import RequestException, Response
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from dispatcher.db import async_session_factory
from dispatcher.db.models import LinkdingDBBookmark
from dispatcher.services.user_service import UserService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


PREVIEW_DIR = Path(
    os.getenv("LINKDING_PREVIEW_DIR", "/tmp/linkding-favicons")
).resolve()


async def _get_bookmark(
    session: AsyncSession, user_id: int, bookmark_id: int
) -> LinkdingDBBookmark | None:
    query = (
        select(LinkdingDBBookmark)
        .filter(LinkdingDBBookmark.owner_id == user_id)
        .filter(LinkdingDBBookmark.id == bookmark_id)
    )

    db_bookmark_result = await session.execute(query)
    db_bookmark = db_bookmark_result.scalar()

    return db_bookmark


def _build_preview_filename(img_url: str, content_type: str | None = None) -> str:
    digest = hashlib.md5(img_url.encode("utf-8")).hexdigest()
    return f"{digest}.png"


def _save_image_to_bytes(img: Image.Image) -> bytes:
    """Helper function to dump Pillow image to bytes."""
    output_buffer = io.BytesIO()
    img.save(output_buffer, format="PNG")
    return output_buffer.getvalue()


def _normilise_image_size(w: int, h: int, boundary: int) -> tuple[int, int]:
    if w > h:
        new_w = boundary
        new_h = int(h * (boundary / w))
    else:
        new_h = boundary
        new_w = int(w * (boundary / h))

    return new_w, new_h


def resize_image_bg(image_bytes: bytes, target_size=(800, 480)):
    target_w, target_h = target_size

    with Image.open(io.BytesIO(image_bytes)) as img:
        img = img.convert("RGBA")
        w, h = img.size

        # if this image is an icon (64, 128), scale it up to 256px:
        if (64 <= w < 256) or (64 <= h < 256):
            new_w, new_h = _normilise_image_size(w, h, 256)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            w, h = img.size  # Update working dimensions

        # If both dimensions fall entirely under 256px or if it is an icon
        # if w < 256 and h < 256 or is_icon:
        #     img.thumbnail(target_size, Image.Resampling.LANCZOS)

        #     new_img = Image.new("RGBA", target_size, (0, 0, 0, 0))
        #     x_offset = (target_w - img.width) // 2
        #     y_offset = (target_h - img.height) // 2
        #     new_img.paste(img, (x_offset, y_offset), img)

        #     return _save_image_to_bytes(new_img)

        # If the image bounds are within this threshold, scale it up first
        if (256 <= w < 512) or (256 <= h < 512):
            new_w, new_h = _normilise_image_size(w, h, 512)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            w, h = img.size  # Update working dimensions

        # At this stage, the image is large enough to be cropped directly to the
        # 100x60 (800x480) aspect ratio without needing a transparent background.
        target_ratio = target_w / target_h
        orig_ratio = w / h

        if orig_ratio > target_ratio:
            scale_h = target_h
            scale_w = int(w * (target_h / h))
        else:
            scale_w = target_w
            scale_h = int(h * (target_w / w))

        # Scale down to matching aspect boundary
        final_img = img.resize((scale_w, scale_h), Image.Resampling.LANCZOS)

        # Calculate coordinates to slice a perfect centered 800x480 box
        left = (scale_w - target_w) // 2
        top = (scale_h - target_h) // 2
        right = left + target_w
        bottom = top + target_h

        cropped_img = final_img.crop((left, top, right, bottom))
        return _save_image_to_bytes(cropped_img)


async def _save_bookmark_preview(
    session: AsyncSession, bookmark: LinkdingDBBookmark, image_url: str, headers: dict
) -> str | None:
    if not image_url:
        return None

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(image_url, follow_redirects=True, headers=headers)
        response.raise_for_status()

        filename = _build_preview_filename(
            image_url, response.headers.get("content-type")
        )
        preview_path = PREVIEW_DIR / filename
        content = resize_image_bg(response.content, target_size=(1280, 768))
        preview_path.write_bytes(content)

        await session.execute(
            update(LinkdingDBBookmark)
            .where(LinkdingDBBookmark.id == bookmark.id)
            .values(preview_image_file=filename)
        )
        await session.commit()

        print(f"->bookmark.id: {bookmark.id}:{filename}")

        return filename


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


def _get_img_url(url: str, html: str) -> str | None:
    image_url = None
    soup = BeautifulSoup(html, "html.parser")
    head = soup.find("head")

    if not head:
        raise Exception("No HEAD was found in HTML")

    meta = (
        head.find("meta", property="og:image")
        or head.find("meta", property="eb:image")
        or head.find("meta", property="og:image:secure_url")
        or head.find("meta", property="twitter:image")
        or head.find("meta", attrs={"itemprop": "image"})
        or head.find("link", attrs={"rel": "preload", "as": "image"})
        or head.find("meta", attrs={"rel": "apple-touch-icon", "sizes": "512x512"})
        or head.find("meta", attrs={"rel": "apple-touch-icon", "sizes": "256x256"})
        or head.find("link", attrs={"rel": "icon", "sizes": "256x256"})
        or head.find("meta", attrs={"rel": "apple-touch-icon", "sizes": "180x180"})
        or head.find("link", attrs={"rel": "icon", "sizes": "180x180"})
        or head.find("meta", attrs={"rel": "apple-touch-icon", "sizes": "152x152"})
        or head.find("link", attrs={"rel": "icon", "sizes": "152x152"})
        or head.find("link", attrs={"rel": "icon", "sizes": "128x128"})
        or head.find("link", attrs={"rel": "icon", "sizes": "64x64"})
    )

    if meta and meta.name == "link" and meta.get("as") == "image":
        imagesrcset = meta.get("imagesrcset")

        if isinstance(imagesrcset, str) and imagesrcset:
            candidates = [item.strip() for item in imagesrcset.split(",")]

            if candidates:
                candidate_urls = [c.split()[0] for c in candidates if c]

                if candidate_urls:
                    image_url = candidate_urls[-1]
        elif meta.has_attr("href"):
            image_url = str(meta.get("href"))
    elif meta and meta.has_attr("href"):
        image_url = str(meta.get("href"))
    elif meta and meta.has_attr("content"):
        image_url = str(meta.get("content"))

    if image_url:
        return str(urljoin(url, image_url))

    return None


def _get_html(response: Response) -> str:
    content_encoding = str(response.headers.get("content-encoding", "")).lower()
    html = response.text

    try:
        if "gzip" in content_encoding:
            import gzip

            html = gzip.decompress(response.content).decode(
                response.encoding or "utf-8", errors="ignore"
            )
        elif "br" in content_encoding:
            import brotli

            html = brotli.decompress(response.content).decode(
                response.encoding or "utf-8", errors="ignore"
            )
        elif "deflate" in content_encoding:
            import zlib

            html = zlib.decompress(response.content).decode(
                response.encoding or "utf-8", errors="ignore"
            )
    except Exception:
        if "html" not in html:
            logger.warning(f"Cannot decode HTML {content_encoding}:{response.url}")

            # if content_encoding == "br":
            logger.warning(response.content[:150])
            logger.warning("----------------")

    return html


async def _process_bookmark_image(
    session: AsyncSession, scraper: CloudScraper, bookmark: LinkdingDBBookmark
):
    headers = _get_headers(bookmark.url)
    response = scraper.get(bookmark.url, headers=headers, allow_redirects=True)

    response.raise_for_status()

    html = _get_html(response)
    img_url = _get_img_url(str(response.url), html)
    headers.update({"Referer": bookmark.url})

    print(f"img_url: {img_url}")

    if img_url:
        saved_filename = await _save_bookmark_preview(
            session,
            bookmark,
            img_url,
            headers,
        )
        logger.info(f"Bookmark image updated: {saved_filename}")
    else:
        logger.warning(f"No image URL found for {response.url}")


async def process_bookmark_image(ctx: dict, token: str, bookmark_id: int) -> bool:
    print("--- process_bookmark_image ---")
    print(f"token: {token}")
    print(f"bookmark_id: {bookmark_id}")
    print("")

    user = await UserService.get_user(token)

    if not user:
        logger.warning("User not found")
        return False

    async with async_session_factory() as session:
        scraper = cloudscraper.create_scraper()
        bookmark = await _get_bookmark(session, user.id, bookmark_id)

        if bookmark and not bookmark.preview_image_file:
            try:
                await _process_bookmark_image(session, scraper, bookmark)
            except (httpx.HTTPError, RequestException) as exc:
                logger.warning(
                    f"Failed fetching bookmark Info {bookmark.id}:{bookmark.url}\n{exc}"
                )
            except Exception as ex:
                logger.warning(f"Failed updating bookmark: {bookmark.id}:\n{ex}")
        elif bookmark:
            logger.info(f"Bookmark already has an image: {bookmark.preview_image_file}")

    print("")

    return True
