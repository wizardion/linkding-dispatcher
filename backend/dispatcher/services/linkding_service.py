import logging
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

import httpx

from dispatcher.core.settings import LinkdingSettings
from dispatcher.schemas.bookmark import Bookmark, LinkdingBookmark, Metadata

logger = logging.getLogger(__name__)


class LinkdingService:
    def __init__(
        self,
        token: str,
        settings: LinkdingSettings,
        bundles_set: set[str] | None = None,
    ):
        self.linkding_token = token
        self.linkding_url = settings.linkding_url
        self.bundles_set = bundles_set or set()
        self.api_endpoint = f"{self.linkding_url}/api/bookmarks"

    @classmethod
    def encode_url(cls, url: str) -> str:
        split_url = urlsplit(url)
        escaped_path = quote(split_url.path, safe="/")
        query_params = parse_qsl(split_url.query)
        escaped_query = urlencode(query_params)

        return urlunsplit(
            (
                split_url.scheme,
                split_url.netloc,
                escaped_path,
                escaped_query,
                split_url.fragment,
            )
        )

    async def check_bookmark(self, url: str) -> tuple[Bookmark | None, Metadata | None]:
        headers = {"Authorization": f"Token {self.linkding_token}"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_endpoint}/check/?url={self.encode_url(url)}",
                    headers=headers,
                    timeout=5.0,
                )

                if response.status_code != 200:
                    raise Exception("Checking resource failed.")

                data: dict[str, dict] = response.json()
                bookmark_data: dict | None = data.get("bookmark")
                metadata: dict | None = data.get("metadata")

                if bookmark_data:
                    bokmark_tags = set(bookmark_data.get("tag_names", []))

                    bookmark = Bookmark(
                        id=bookmark_data["id"],
                        url=bookmark_data["url"],
                        title=bookmark_data["title"],
                        description=bookmark_data["description"],
                        is_archived=bookmark_data["is_archived"],
                        bundle=" ".join(bokmark_tags & self.bundles_set),
                        tag_names=list(bokmark_tags - self.bundles_set),
                    )

                    return (
                        bookmark,
                        Metadata.model_validate(metadata) if metadata else None,
                    )

                return (None, Metadata.model_validate(metadata) if metadata else None)
        except Exception as ex:
            logger.error(f"Checking resource failed. {ex}")

        return None, None

    async def save_bookmark(self, model: LinkdingBookmark) -> LinkdingBookmark | None:
        headers = {"Authorization": f"Token {self.linkding_token}"}
        model_id = str(model.id) + "/" if model.id else ""
        request_url = f"{self.linkding_url}/api/bookmarks/{model_id}"
        method = "PUT" if model.id else "POST"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method,
                    request_url,
                    json=model.model_dump(by_alias=True),
                    headers=headers,
                )
                data = response.json()

                if response.status_code not in [200, 201]:
                    error = ""
                    details = data.get("detail", {})

                    if isinstance(details, str):
                        error = details
                    elif isinstance(details, dict):
                        error = details.get("msg", data)

                    logger.error(f"Saving bookmark failed. {error}")

                    return None

                return LinkdingBookmark.model_validate(data)

        except Exception as ex:
            logger.error(f"Saving bookmark failed. {ex}")

        return None

    async def remove_bookmark(self, id: int) -> bool:
        headers = {"Authorization": f"Token {self.linkding_token}"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(
                    f"{self.linkding_url}/api/bookmarks/{id}/", headers=headers
                )

                if response.status_code not in [204, 200]:
                    data = response.json()
                    logger.error(f"Failed to delete bookmark. {data}")
                    return False

                return True
            except Exception as ex:
                logger.error(f"Failed to delete bookmark. {ex}")
                return False
