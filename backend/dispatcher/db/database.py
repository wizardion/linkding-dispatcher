from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from dispatcher.core import settings

# Gather configuration from your existing Docker Compose environment variables
DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{settings.database.db_user}:{settings.database.db_password}"
    f"@{settings.database.db_host}:{settings.database.db_port}/"
    f"{settings.database.db_name}"
)

async_engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

async_session_factory = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)
