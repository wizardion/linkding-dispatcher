from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

Base = declarative_base()


class LinkdingDBUser(Base):
    __tablename__ = "auth_user"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False)
    first_name: Mapped[str] = mapped_column(String(150), nullable=False)
    last_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)


class LinkdingDBApiToken(Base):
    __tablename__ = "bookmarks_apitoken"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("auth_user.id"))


class LinkdingDBBookmark(Base):
    __tablename__ = "bookmarks_bookmark"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    website_title: Mapped[str | None] = mapped_column(String(512))
    website_description: Mapped[str | None] = mapped_column(Text)
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False)
    url_normalized: Mapped[str] = mapped_column(String(2048), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("auth_user.id"))


class LinkdingDBBundle(Base):
    __tablename__ = "bookmarks_bookmarkbundle"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    all_tags: Mapped[str] = mapped_column(String(1024), nullable=False)
    order: Mapped[int] = mapped_column(nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("auth_user.id"))


class LinkdingDBTag(Base):
    __tablename__ = "bookmarks_tag"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    date_added: Mapped[datetime] = mapped_column(
        DateTime(), default=lambda: datetime.now(UTC), nullable=False
    )
    owner_id: Mapped[int] = mapped_column(ForeignKey("auth_user.id"))


class LinkdingDBBookmarkTag(Base):
    __tablename__ = "bookmarks_bookmark_tags"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    bookmark_id: Mapped[int] = mapped_column(ForeignKey("bookmarks_bookmark.id"))
    tag_id: Mapped[int] = mapped_column(ForeignKey("bookmarks_tag.id"))
