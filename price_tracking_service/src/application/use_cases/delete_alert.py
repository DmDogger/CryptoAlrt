"""Use case for deleting user alert.

Deletes alert by ID, ensuring it belongs to the specified email.
"""

import uuid

import structlog
from sqlalchemy.exc import SQLAlchemyError

from application.interfaces.repositories import AlertRepositoryProtocol
from domain.exceptions import AlertNotFound

logger = structlog.getLogger(__name__)


class DeleteAlertUseCase:
    """Use case for deleting an alert that belongs to a specific user."""

    def __init__(self, repository: AlertRepositoryProtocol):
        self._repository = repository

    async def execute(
        self,
        alert_id: uuid.UUID,
        email: str,
    ):
        """Delete alert by id ensuring it belongs to the provided email."""
        try:
            logger.debug(
                "Starting to get information about alert",
                alert_id=alert_id,
                email=email,
            )
            alert_exist = await self._repository.get_alert_by_id(alert_id)

            if not alert_exist:
                logger.error(
                    "Alert not found",
                    alert_id=alert_id,
                    email=email,
                )

                raise AlertNotFound(f"Alert with ID: {alert_id} not found.")

            logger.info(
                "Deleting alert",
                alert_id=alert_id,
                email=email,
            )

            await self._repository.delete_alert_by_id(
                email=email,
                alert_id=alert_exist.id,
            )

        except (SQLAlchemyError, Exception) as e:
            logger.error(
                "Error occurred during deleting alert",
                error=str(e),
                exc_info=True,
                error_type=type(e).__name__,
            )
            raise
