from typing import final

from pydantic import Field
from pydantic_settings import BaseSettings


@final
class CoinGeckoSettings(BaseSettings):
    base_url: str = Field(default="https://api.coingecko.com/api/v3/")
    headers: dict = {
        'x-cg-demo-api-key': 'CG-popCvCELuaAkMvM6utrfhJwp',
    }
    params: dict = {
        "vs_currencies": "usd"
    }

coingecko_settings = CoinGeckoSettings()