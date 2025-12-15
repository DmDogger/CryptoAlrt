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
            logger.info(f"Start to getting information about alert with ID: {alert_id} for {email}")
            alert_exist = await self._repository.get_alert_by_id(alert_id)

            if not alert_exist:
                logger.error(f"Alert with ID: {alert_id} for {email} not found")
                raise AlertNotFound(f"Alert with ID: {alert_id} not found.")
            logger.info(f"Alert with ID: {alert_id} for {email} found")


            logger.info(f"Trying to delete alert with id {alert_exist.id} for {email}")
            await self._repository.delete_alert_by_id(
                email=email,
                alert_id=alert_exist.id,
            )
            logger.info(f"Alert deleted successfully")

        except (SQLAlchemyError, Exception) as e:
            logger.error(
                f"Occurred error ({e}) with deleting alert for {email} with {alert_exist.id}"
            )
            raise




