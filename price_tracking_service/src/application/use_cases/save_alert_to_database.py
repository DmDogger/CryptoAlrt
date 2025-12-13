from decimal import Decimal
from uuid import UUID

import structlog

from src.application.interfaces.repositories import AlertRepositoryProtocol
from src.domain.entities.alert import AlertEntity
from src.domain.exceptions import AlertSavingError

logger = structlog.getLogger(__name__)


class SaveAlertToDBUseCase:
    def __init__(
            self,
            alert_repository: AlertRepositoryProtocol,
    ):
        self._alert_repository = alert_repository

    async def execute(
            self,
            email: str,
            cryptocurrency: str,
            threshold_price: Decimal,
            cryptocurrency_id: UUID,
            is_active: bool = True,
    ) -> None:
        """Creates and saves alert entity to database.

        Args:
            email: User's email.
            cryptocurrency: Cryptocurrency symbol.
            threshold_price: Threshold price value.
            cryptocurrency_id: ID of the cryptocurrency.
            is_active: Whether the alert is active.

        Raises:
            AlertSavingError: If saving fails.
        """
        try:
            alert = AlertEntity.create(
                email=email,
                cryptocurrency=cryptocurrency,
                threshold_price=threshold_price,
                is_active=is_active,
            )
            await self._alert_repository.save(
                cryptocurrency_id=cryptocurrency_id,
                alert=alert
            )
            logger.info(f"[Success]: Alert with ID {alert.id} saved successfully")

        except Exception as e:
            logger.error(f"[Error]: Failed to save alert with ID {alert.id}: {e}")
            raise AlertSavingError(f"Failed to save alert: {e}") from e