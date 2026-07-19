import functools
import logging
from collections.abc import Callable
from inspect import Signature, signature

from pydantic import TypeAdapter

from .cache_manager import CacheManager, CacheStrategy
from .dependencies import cache_manager as default_cache_manager

logger = logging.getLogger(__name__)


def db_cache(
    key_builder: Callable[..., str],
    strategy: CacheStrategy = CacheStrategy.ONE_DAY,
    cache_manager: CacheManager = default_cache_manager,
):
    def decorator(func):
        sig = signature(func)
        return_type = sig.return_annotation
        adapter = (
            TypeAdapter(return_type) if return_type is not Signature.empty else None
        )

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = key_builder(*args, **kwargs)

            try:
                cached_bytes = await cache_manager.get_binary(cache_key)

                if cached_bytes and adapter:
                    return adapter.validate_json(cached_bytes)
            except Exception as e:
                logger.error(f"Cache read error.  {e}")

            result = await func(*args)

            try:
                if adapter and result is not None:
                    serialized_bytes = adapter.dump_json(result)

                    await cache_manager.set_binary(
                        cache_key, serialized_bytes, strategy=strategy
                    )
            except Exception as e:
                logger.error(f"Cache write error. {e}")

            return result

        return wrapper

    return decorator


# def instance_cache(func):
#     """
#     Caches the output of an async method inside the 'self' instance memory.
#     The cache naturally dies whenever the class instance is garbage collected.
#     """

#     @functools.wraps(func)
#     async def wrapper(self, *args, **kwargs):
#         # 1. Dynamically initialize a private cache dictionary on the instance
#         # if it doesn't exist
#         if not hasattr(self, "_instance_mem_cache"):
#             self._instance_mem_cache = {}

#         # 2. Generate a cache key from arguments (ignoring 'self')
#         # We turn kwargs into a sorted tuple so it's hashable
#         cache_key = (func.__name__, args, tuple(sorted(kwargs.items())))

#         # 3. Cache Hit
#         if cache_key in self._instance_mem_cache:
#             return self._instance_mem_cache[cache_key]

#         # 4. Cache Miss: Execute the actual underlying method
#         result = await func(self, *args, **kwargs)

#         # 5. Save the live Python object straight to memory
#         self._instance_mem_cache[cache_key] = result

#         return result

#     return wrapper
