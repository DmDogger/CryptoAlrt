from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol, final

import httpx

from application.dtos.coingecko_object import CoinGeckoDTO


class CoinGeckoClientProtocol(Protocol):
    @abstractmethod
    async def fetch_price(self, symbol: str) -> CoinGeckoDTO: ...
