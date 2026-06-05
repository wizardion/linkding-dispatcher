import asyncio
import logging
from typing import Any
from cache_manager import CacheManager, CacheStrategy
from urllib.parse import urlsplit, urlunsplit, quote, urlencode, parse_qsl
import httpx

logger = logging.getLogger(__name__)

def encode_url(url: str) -> str:
    split_url = urlsplit(url)
    escaped_path = quote(split_url.path, safe='/')
    query_params = parse_qsl(split_url.query)
    escaped_query = urlencode(query_params)

    
    return urlunsplit((
        split_url.scheme,
        split_url.netloc,
        escaped_path,
        escaped_query,
        split_url.fragment
    ))

async def get_tags(cache: CacheManager, linkding_url: str, token: str) -> list[str]:
    headers = {"Authorization": f"Token {token}"}
    try:
        tags = await cache.get("linkding:tags")

        if tags is None:
            client = httpx.AsyncClient()
            response = await client.get(f"{linkding_url}/api/tags/", headers=headers, timeout=5.0)
            results = response.json().get("results", [])

            if isinstance(results, list):
                tags = [x["name"] for x in results if x.get("name")]
                await cache.set("linkding:tags", tags, CacheStrategy.ONE_WEEK)

        return tags
    except Exception:
        logger.exception("Tags resolution failed")
        return []


async def get_bundles(cache: CacheManager, linkding_url: str, token: str) -> list[dict[str, Any]]:
    headers = {"Authorization": f"Token {token}"}
    try:
        bundles = await cache.get("linkding:bundles")

        if bundles is None:
            client = httpx.AsyncClient()
            response = await client.get(f"{linkding_url}/api/bundles/", headers=headers, timeout=5.0)
            results = response.json().get("results", [])

            if isinstance(results, list):
                bundles = results
                await cache.set("linkding:bundles", bundles, CacheStrategy.ONE_WEEK)

        return bundles
    except Exception:
        logger.exception("Bundles resolution failed")
        return []


async def check_url(
    url: str, 
    linkding_url: str, 
    token: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    headers = {"Authorization": f"Token {token}"}
    try:
        if url:
            client = httpx.AsyncClient()
            response = await client.get(
                f"{linkding_url}/api/bookmarks/check/?url={encode_url(url)}", 
                headers=headers, 
                timeout=5.0
            )

            data = response.json()
            bookmark_data = data.get("bookmark")
            metadata = data.get("metadata")

            return bookmark_data, metadata
        else:
            return {}, {}
    except Exception:
        logger.exception("Bundles resolution failed")
        return {}, {}
