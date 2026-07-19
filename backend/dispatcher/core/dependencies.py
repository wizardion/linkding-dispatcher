from .cache_manager import CacheManager
from .settings import Settings

settings = Settings()
cache_manager = CacheManager(settings=settings.memcache)
