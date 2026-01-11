from typing import final

from pydantic import Field
from pydantic_settings import BaseSettings


@final
class CacheSettings(BaseSettings):
    cache_version: str = Field(default="1", alias="CACHE_VERSION")
    key_expire: int = Field(default=60**2, alias="KEY_EXPIRE")  # one hour
    max_size: int = Field(default=50 * 1024 * 1024)  # 50 mb


cache_settings = CacheSettings()
