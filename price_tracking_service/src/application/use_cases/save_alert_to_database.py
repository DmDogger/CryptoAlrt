"""Use case for saving new alert to database.

Creates and persists user alert with specified parameters (cryptocurrency, threshold, email).
"""

from decimal import Decimal
from uuid import UUID

import structlog

from application.interfaces.repositories import (
    AlertRepositoryProtocol,
    CryptocurrencyRepositoryProtocol,
)
from domain.exceptions import AlertSavingError, CryptocurrencyNotFound
from presentation.api.v1.mappers.to_response import AlertPresentationMapper
from presentation.api.v1.schemas.alert import AlertCreateRequest

logger = structlog.getLogger(__name__)


class SaveAlertToDBUseCase:
    def __init__(
        self,
        alert_repository: AlertRepositoryProtocol,
        cryptocurrency_repository: CryptocurrencyRepositoryProtocol,
        mapper: AlertPresentationMapper,
    ):
        self._alert_repository = alert_repository
        self._cryptocurrency_repository = cryptocurrency_repository
        self._mapper = mapper

    async def execute(
        self,
        alert_pydantic: AlertCreateRequest,
    ) -> None:
        """Creates and saves alert entity to database."""
        try:
            cryptocurrency = (
                await self._cryptocurrency_repository.get_cryptocurrency_by_coingecko_id(
                    alert_pydantic.cryptocurrency_slug
                )
            )

            if not cryptocurrency:
                raise CryptocurrencyNotFound(
                    f"Cryptocurrency with slug '{alert_pydantic.cryptocurrency_slug}' not found"
                )

            alert = self._mapper.from_pydantic_to_entity(alert_pydantic)
            await self._alert_repository.save(cryptocurrency_id=cryptocurrency.id, alert=alert)
            logger.info(
                "Alert saved",
                email=alert_pydantic.email,
            )

        except Exception as e:
            logger.error(
                "Failed to save alert",
                email=alert_pydantic.email,
                error=str(e),
                exc_info=True,
            )
            raise AlertSavingError(f"Failed to save alert: {e}") from e
