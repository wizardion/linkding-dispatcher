from collections.abc import AsyncGenerator

from arq import ArqRedis
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from dispatcher.db import async_session_factory
from dispatcher.schemas.user import AuthUser
from dispatcher.services import BookmarkService, UserSessionService


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        yield session


async def get_user(request: Request) -> AsyncGenerator[AuthUser]:
    return request.user


async def get_arq_pool(request: Request) -> AsyncGenerator[ArqRedis]:
    return request.app.state.arq_pool


def get_bookmark_service(request: Request) -> BookmarkService:
    """
    Factory function providing a fresh, request-scoped BookmarkService instance.
    """
    return BookmarkService(request.user)


def get_session_service(request: Request) -> UserSessionService:
    """
    Factory function providing a fresh, request-scoped BookmarkService instance.
    """
    return UserSessionService(request.user)
