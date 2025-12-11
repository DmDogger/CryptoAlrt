from abc import abstractmethod
from typing import Protocol
from uuid import UUID

from domain.entities.alert import AlertEntity
from domain.entities.cryptocurrency import CryptocurrencyEntity


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
    async def save(self, alert: AlertEntity) -> None:
        ...


class CryptocurrencyRepositoryProtocol(Protocol):
    """
    Protocol for a cryptocurrency repository.
    Defines methods for retrieving and saving cryptocurrency entities.
    """
    @abstractmethod
    async def get_by_cryptocurrency_id(
        self, cryptocurrency_id: str | UUID
    ) -> CryptocurrencyEntity | None:
        ...

    @abstractmethod
    async def save(self, artifact: CryptocurrencyEntity) -> None:
        ...