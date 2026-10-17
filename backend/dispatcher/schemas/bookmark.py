from pydantic import BaseModel, ConfigDict, Field, field_validator

from dispatcher.core import encode_url


class LinkdingBookmark(BaseModel):
    model_config = ConfigDict(validate_by_name=True)

    id: int | None = None
    url: str
    title: str
    tags: list[str] = Field(alias="tag_names")
    archived: bool = Field(default=False, alias="is_archived")
    description: str | None = None
    preview_image_url: str | None = None

    @field_validator("url", mode="before")
    @classmethod
    def override_url_validation(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            raise Exception("Url is not valid")

        return encode_url(value.strip().lower())


class Bookmark(LinkdingBookmark):
    bundle: str | None = None


class BookmarkPayload(Bookmark):
    remember: bool = False


class Metadata(BaseModel):
    url: str | None = None
    title: str | None = None
    description: str | None = None
