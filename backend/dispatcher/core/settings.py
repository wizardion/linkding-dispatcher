from enum import IntEnum

from pydantic_settings import BaseSettings


class CacheStrategy(IntEnum):
    ONE_DAY = 86400
    ONE_WEEK = 604800
    ONE_MONTH = 2592000


class MemcacheSettings(BaseSettings):
    memcache_host: str = ""
    memcache_port: int = 11211
    cache_logging_enabled: bool = True


class RedisSettings(BaseSettings):
    redis_host: str = ""
    redis_port: int = 6379


class DatabseSettings(BaseSettings):
    db_host: str = "linkding_db"
    db_port: int = 5432
    db_user: str = "linkding"
    db_password: str = ""
    db_name: str = "linkding"


class LinkdingSettings(BaseSettings):
    linkding_host: str = ""
    linkding_port: int = 8000
    linkding_schema: str = "HTTP"

    @property
    def linkding_url(self) -> str:
        return (
            f"{self.linkding_schema.lower()}://{self.linkding_host}"
            f":{self.linkding_port}"
        )


class Settings(BaseSettings):
    linkding: LinkdingSettings = LinkdingSettings()
    memcache: MemcacheSettings = MemcacheSettings()
    database: DatabseSettings = DatabseSettings()
    redis: RedisSettings = RedisSettings()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
