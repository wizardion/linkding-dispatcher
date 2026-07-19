from contextlib import asynccontextmanager

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI

from .dependencies import cache_manager, settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.arq_pool = await create_pool(
        RedisSettings(host=settings.redis.redis_host, port=settings.redis.redis_port)
    )

    await cache_manager.connect()

    yield

    await app.state.arq_pool.close()
    await cache_manager.disconnect()
