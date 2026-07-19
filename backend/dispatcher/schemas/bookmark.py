from pydantic import BaseModel, ConfigDict, Field


class LinkdingBookmark(BaseModel):
    model_config = ConfigDict(validate_by_name=True)

    id: int | None = None
    url: str
    title: str
    tags: list[str] = Field(alias="tag_names")
    archived: bool = Field(default=False, alias="is_archived")
    description: str | None = None


class Bookmark(LinkdingBookmark):
    bundle: str | None = None


class BookmarkPayload(Bookmark):
    remember: bool = False


class Metadata(BaseModel):
    url: str | None = None
    title: str | None = None
    description: str | None = None
