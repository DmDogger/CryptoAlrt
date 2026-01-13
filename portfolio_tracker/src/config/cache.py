from typing import final

from pydantic import Field
from pydantic_settings import BaseSettings


@final
class CacheSettings(BaseSettings):
    cache_version: str = Field(default="1", alias="CACHE_VERSION")
    key_expire: int = Field(default=60**2, alias="KEY_EXPIRE")  # one hour
    max_size: int = Field(default=50 * 1024 * 1024)  # 50 mb
    version_with_assets_and_prices: str = Field(default="with_assets_and_prices")
    version_portfolio_total_value: str = Field(default="get_portfolio_total_value")
    version_total_value: str = Field(default="only_total_value")
    assets_counted: str = Field(default="assets_counted")
    portfolio_assotiated_with_assets_counted: str = Field(
        default="portfolio_assotiated_with_assets_counted"
    )


cache_settings = CacheSettings()
