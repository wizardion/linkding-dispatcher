from arq.connections import RedisSettings
from arq.worker import func

from dispatcher.core import settings

from .image_bookmark import process_bookmark_image
from .remove_bookmark import process_bookmark_remove
from .save_bookmark import process_bookmark_save
from .tasks import process_all_bookmark_image


class WorkerSettings:
    functions = [
        func(process_bookmark_save, name="process_bookmark:save"),
        func(process_bookmark_remove, name="process_bookmark:remove"),
        func(process_all_bookmark_image, name="process_bookmark:images", timeout=18000),
        func(process_bookmark_image, name="process_bookmark:image", timeout=18000),
    ]
    # cron_jobs = [
    #     cron(process_bookmark_image, hour=2, minute=0, timeout=18000),
    # ]
    redis_settings = RedisSettings(
        host=settings.redis.redis_host, port=settings.redis.redis_port
    )
