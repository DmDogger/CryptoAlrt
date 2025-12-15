from decimal import Decimal
from uuid import UUID

import structlog

from application.interfaces.repositories import AlertRepositoryProtocol, CryptocurrencyRepositoryProtocol
from domain.entities.alert import AlertEntity
from domain.entities.cryptocurrency import CryptocurrencyEntity
from domain.exceptions import AlertSavingError, CryptocurrencyNotFound
from presentation.api.v1.mappers.to_response import AlertPresentationMapper
from presentation.api.v1.schemas.alert import AlertCreateRequest

logger = structlog.getLogger(__name__)


class SaveAlertToDBUseCase:
    def __init__(
            self,
            alert_repository: AlertRepositoryProtocol,
            cryptocurrency_repository: CryptocurrencyRepositoryProtocol,
            mapper: AlertPresentationMapper
    ):
        self._alert_repository = alert_repository
        self._cryptocurrency_repository = cryptocurrency_repository
        self._mapper = mapper

    async def execute(
            self,
            alert_pydantic: AlertCreateRequest,
    ) -> None:
        """Creates and saves alert entity to database.

        Args:


        Raises:
            AlertSavingError: If saving fails.
        """
        try:
            cryptocurrency = await self._cryptocurrency_repository.get_cryptocurrency_by_coingecko_id(
                alert_pydantic.cryptocurrency_slug
            )

            if not cryptocurrency:
                raise CryptocurrencyNotFound(
                    f"Cryptocurrency with slug '{alert_pydantic.cryptocurrency_slug}' not found"
                )

            alert = self._mapper.from_pydantic_to_entity(alert_pydantic)
            await self._alert_repository.save(
                cryptocurrency_id=cryptocurrency.id,
                alert=alert
            )
            logger.info(f"[Success]: Alert with email: {alert_pydantic.email} saved successfully")

        except Exception as e:
            logger.error(f"[Error]: Failed to save alert with ID {alert_pydantic.email}: {e}")
            raise AlertSavingError(f"Failed to save alert: {e}") from e