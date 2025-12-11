from uuid import UUID

import structlog

from application.interfaces.repositories import AlertRepositoryProtocol
from domain.entities.alert import AlertEntity
from domain.exceptions import AlertSavingError

logger = structlog.getLogger(__name__)


class SaveAlertToDBUseCase:
    def __init__(
            self,
            alert_repository: AlertRepositoryProtocol,
    ):
        self._alert_repository = alert_repository

    async def execute(
            self,
            alert: AlertEntity,
            cryptocurrency_id: UUID,
    ) -> None:
        """Saves alert entity to database.

        Args:
            alert: AlertEntity to save.
            cryptocurrency_id: ID of the cryptocurrency.

        Raises:
            AlertSavingError: If saving fails.
        """
        try:
            await self._alert_repository.save(
                cryptocurrency_id=cryptocurrency_id,
                alert=alert
            )
            logger.info(f"[Success]: Alert with ID {alert.id} saved successfully")

        except Exception as e:
            logger.error(f"[Error]: Failed to save alert with ID {alert.id}: {e}")
            raise AlertSavingError(f"Failed to save alert: {e}") from e