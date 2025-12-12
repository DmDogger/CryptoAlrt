from abc import abstractmethod
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from src.domain.entities.alert import AlertEntity
from src.domain.entities.cryptocurrency import CryptocurrencyEntity
from src.application.dtos.coingecko_object import CoinGeckoDTO


class AlertRepositoryProtocol(Protocol):
    """
    Protocol for an alert repository.
    Defines methods for retrieving and saving alert entities.
    """
    @abstractmethod
    async def get_alert_by_id(
        self, alert_id: str | UUID
    ) -> AlertEntity | None:
        ...

    @abstractmethod
    async def save(self, cryptocurrency_id: UUID, alert: AlertEntity) -> None:
        ...


class CryptocurrencyRepositoryProtocol(Protocol):
    """
    Protocol for a cryptocurrency repository.
    Defines methods for retrieving and saving cryptocurrency entities.
    """

    @abstractmethod
    async def get_last_price(
            self, cryptocurrency_id: str | UUID
    ) -> Decimal | None:
        ...

    @abstractmethod
    async def get_by_cryptocurrency_id(
        self, cryptocurrency_id: str | UUID
    ) -> CryptocurrencyEntity | None:
        ...

    @abstractmethod
    async def save(self, crypto: CryptocurrencyEntity) -> None:
        ...

    @abstractmethod
    async def save_price(
            self,
            cryptocurrency_id: UUID,
            price_data: CoinGeckoDTO
    ) -> None: ...

    @abstractmethod
    async def get_cryptocurrency_by_symbol(self, symbol: str) -> CryptocurrencyEntity | None: ...

    @abstractmethod
    async def get_cryptocoins_list_by_coingecko_id(
            self,
            coingecko_id: str
    ) -> list[CryptocurrencyEntity]: ...