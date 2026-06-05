import os
import json
import logging
import emcache
from enum import IntEnum

# Configure standard logging
# To reset the cache, you can run this module directly: 
# `docker exec -it linkding_memcached sh -c "echo 'flush_all' | nc 127.0.0.1 11211"`
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CacheManager")

class CacheStrategy(IntEnum):
    ONE_DAY = 86400
    ONE_WEEK = 604800
    ONE_MONTH = 2592000

class CacheManager:
    def __init__(self):
        self.host = os.getenv("MEMCACHE_HOST", "127.0.0.1")
        self.port = int(os.getenv("MEMCACHE_PORT", 11211))
        self.log_enabled = os.getenv("CACHE_LOGGING_ENABLED", "true").lower() == "true"
        self.client = None
        
    async def _connect(self):
        """Lazy-loads the Cythonized emcache connection pool."""
        if not self.client:
            self.client = await emcache.create_client([
                emcache.MemcachedHostAddress(self.host, self.port)
            ])
            if self.log_enabled:
                logger.info(f"Connected to Memcached via emcache at {self.host}:{self.port}")

    def _log(self, msg: str):
        if self.log_enabled:
            logger.info(msg)

    async def get(self, key: str):
        """Fetch and deserialize JSON data from cache."""
        await self._connect()
        
        # emcache returns an Item object, the raw bytes are in item.value
        item = await self.client.get(key.encode('utf-8'))
        if item:
            self._log(f"HIT: {key}")
            return json.loads(item.value.decode('utf-8'))
        
        self._log(f"MISS: {key}")
        return None

    async def set(self, key: str, value: dict | list, strategy: CacheStrategy = CacheStrategy.ONE_DAY):
        """Serialize JSON data and store with a specific TTL Enum strategy."""
        await self._connect()
        
        self._log(f"SET: {key} (TTL: {strategy.name})")
        payload = json.dumps(value).encode('utf-8')
        
        # emcache natively supports the exptime kwarg
        await self.client.set(key.encode('utf-8'), payload, exptime=strategy.value)

    async def reset(self):
        """Flush the entire cache instantly."""
        await self._connect()
        self._log("FLUSHING ENTIRE CACHE")
        await self.client.flush_all()