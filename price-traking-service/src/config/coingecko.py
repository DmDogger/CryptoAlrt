from typing import final

from pydantic import Field
from pydantic_settings import BaseSettings


@final
class CoinGeckoSettings(BaseSettings):
    base_url: str = Field(default="https://api.coingecko.com/api/coin/simple/")