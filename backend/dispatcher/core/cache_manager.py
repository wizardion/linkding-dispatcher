import logging

import emcache
from emcache import Client, MemcachedHostAddress, StorageCommandError

from .settings import CacheStrategy, MemcacheSettings

# To reset the cache, you can run this module directly:
# `docker exec -it linkding_memcached sh -c "echo 'flush_all' | nc 127.0.0.1 11211"`
logger = logging.getLogger(__name__)


class CacheManager:
    def __init__(self, settings: MemcacheSettings):
        self._client: Client | None = None
        self.host = settings.memcache_host
        self.port = settings.memcache_port
        self.log_enabled = settings.cache_logging_enabled

    async def connect(self) -> Client:
        """Lazy-loads the Cythonized emcache connection pool."""
        if not self._client:
            self._client = await emcache.create_client(
                [MemcachedHostAddress(self.host, self.port)]
            )
            if self.log_enabled:
                logger.info(
                    f"Connected to Memcached via emcache at {self.host}:{self.port}"
                )

        return self._client

    async def disconnect(self):
        if self._client:
            await self._client.close()

    async def get_binary(self, key: str) -> bytes | None:
        """Fetched data from cache in binary."""
        client = await self.connect()
        item = await client.get(key.encode("utf-8"))

        return item.value if item else None

    async def set_binary(
        self,
        key: str,
        payload: bytes,
        strategy: CacheStrategy = CacheStrategy.ONE_DAY,
    ) -> bool:
        """Sets binary data with a specific TTL Enum strategy."""
        try:
            client = await self.connect()

            await client.set(key.encode("utf-8"), payload, exptime=strategy.value)
            return True
        except StorageCommandError as ex:
            logger.info(f"Cache storage error: {ex}")

        return False

    async def reset(self, key: str | None = None) -> bool:
        """Flush the cache instantly."""
        try:
            client = await self.connect()

            if key:
                logger.info(f"FLUSHING CACHE: {key}")
                await client.delete(key.encode("utf-8"))
            else:
                logger.info("FLUSHING ENTIRE CACHE")
                await client.flush_all(MemcachedHostAddress(self.host, self.port))

            return True
        except StorageCommandError as ex:
            logger.info(f"Cache storage error: {ex}")
        except Exception as e:
            logger.info(f"Unknown error occurend with cache: {e}")

        return False
