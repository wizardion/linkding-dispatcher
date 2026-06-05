from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    linkding_host: str
    linkding_port: int
    linkding_token: str
    memcache_host: str
    memcache_port: int
    cache_logging_enabled: bool = True

    @property
    def linkding_url(self) -> str:
        return f"http://{self.linkding_host}:{self.linkding_port}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()