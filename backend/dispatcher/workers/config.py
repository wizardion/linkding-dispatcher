from arq.connections import RedisSettings
from arq.worker import func

from dispatcher.core import settings

from .remove_bookmark import process_bookmark_remove
from .save_bookmark import process_bookmark_save


class WorkerSettings:
    functions = [
        func(process_bookmark_save, name="process_bookmark:save"),
        func(process_bookmark_remove, name="process_bookmark:remove"),
    ]
    redis_settings = RedisSettings(
        host=settings.redis.redis_host, port=settings.redis.redis_port
    )
