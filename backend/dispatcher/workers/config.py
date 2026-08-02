from arq.connections import RedisSettings
from arq.worker import func

from dispatcher.core import settings
from dispatcher.workers.tasks import process_bookmark_image

from .remove_bookmark import process_bookmark_remove
from .save_bookmark import process_bookmark_save


class WorkerSettings:
    functions = [
        func(process_bookmark_save, name="process_bookmark:save"),
        func(process_bookmark_remove, name="process_bookmark:remove"),
        func(process_bookmark_image, name="process_bookmark:migrate", timeout=18000),
    ]
    redis_settings = RedisSettings(
        host=settings.redis.redis_host, port=settings.redis.redis_port
    )
