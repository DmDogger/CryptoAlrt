import uuid
from decimal import Decimal

import structlog
from sqlalchemy.exc import SQLAlchemyError

from application.interfaces.repositories import AlertRepositoryProtocol
from domain.entities.alert import AlertEntity
from domain.exceptions import RepositoryError, DomainValidationError, AlertNotFound

logger = structlog.getLogger(__name__)


class UpdateAlertUseCase:
    """
    Use case for updating specific fields of an existing alert in the system.

    This use case handles partial updates of alert entities by accepting individual
    fields to update. It retrieves the existing alert, applies the requested changes
    using domain entity methods, and persists the updated alert.
    """

    def __init__(
            self,
            repository: AlertRepositoryProtocol,
            entity: AlertEntity,
    ):
        """
        Initialize the UpdateAlertUseCase.

        Args:
            repository: The alert repository implementation for data persistence.
        """
        self._repository = repository
        self._entity = entity

    async def execute(
            self,
            cryptocurrency: str | None,
            email: str | None,
            threshold_price: Decimal | None,
            is_active: bool | None,
            alert_id: uuid.UUID,
    ) -> AlertEntity:
        """
        Execute the alert update operation with partial field updates.

        Retrieves the existing alert by ID, applies only the specified field changes
        using domain entity methods, and persists the updated alert. Only non-None
        values trigger updates, and changes are validated through domain logic.

        Args:
            cryptocurrency: New cryptocurrency name to set (optional).
            email: New email address to set (optional).
            threshold_price: New threshold price to set (optional).
            is_active: New active status to set (optional).
            alert_id: The UUID of the alert to update.

        Returns:
            AlertEntity: The updated alert entity from the database.

        Raises:
            AlertNotFound: If the alert with the given ID doesn't exist.
            RepositoryError: If a database operation fails.
            DomainValidationError: If domain business logic validation fails.
        """
        try:
            alert = await self._repository.get_alert_by_id(alert_id)
            if not alert:
                logger.error(f"error alert not found")
                raise AlertNotFound(f"")

            logger.info(
                "Starting alert update operation",
                alert_id=str(alert_id),
                email=alert.email,
                cryptocurrency=str(alert.cryptocurrency),
                threshold_price=str(alert.threshold_price.value),
                is_active=alert.is_active
            )

            if cryptocurrency:
                alert = alert.change_cryptocurrency(cryptocurrency)
            if email:
                alert = alert.change_email(email)
            if threshold_price:
                alert = alert.update_threshold(threshold_price)
            if is_active is False:
                alert = alert.deactivate()


            updated_entity = await self._repository.update(alert)

            logger.info(f"[Info]: Alert ID: {alert_id} updated successfully")

            return updated_entity

        except AlertNotFound as e:
            logger.error(
                "Alert not found during update operation",
                alert_id=str(alert_id),
                error=str(e)
            )
            raise

        except RepositoryError as e:
            logger.error(
                "Repository error during alert update",
                alert_id=str(alert_id),
                error=str(e),
                exc_info=True
            )
            raise

        except SQLAlchemyError as e:
            logger.error(
                "Database error during alert update",
                alert_id=str(alert_id),
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Failed to update alert {alert_id}: database error") from e

        except DomainValidationError as e:
            logger.error(
                "Domain validation error during alert update",
                alert_id=str(alert_id),
                error=str(e),
                exc_info=True
            )
            raise

        except Exception as e:
            logger.error(
                "Unexpected error during alert update",
                alert_id=str(alert_id),
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Unexpected error while updating alert {alert_id}") from e

