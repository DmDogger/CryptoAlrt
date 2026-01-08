"""Use case for retrieving user alerts by email.

Returns all active alerts associated with the specified email address.
"""

from structlog import get_logger

from application.interfaces.repositories import AlertRepositoryProtocol
from domain.entities.alert import AlertEntity
from domain.exceptions import RepositoryError

logger = get_logger(__name__)


class GetAlertsUseCase:
    """Use case for retrieving alerts list by user email.

    This use case encapsulates the business logic for fetching
    all active alerts associated with a specific email address.
    """

    def __init__(self, repository: AlertRepositoryProtocol):
        """Initialize the use case with required dependencies.

        Args:
            repository: Alert repository implementation for data access.
        """
        self._repository = repository

    async def execute(self, email: str) -> list[AlertEntity]:
        """Retrieve all active alerts for a given email address.

        Args:
            email: User's email address to filter alerts.

        Returns:
            List of active AlertEntity objects. Returns empty list if no alerts found.

        Raises:
            RepositoryError: If a database error occurs during retrieval.
            ValueError: If email format is invalid.
        """
        try:
            logger.debug("Executing GetAlertsUseCase", email=email)

            if not email or not isinstance(email, str):
                logger.warning("Invalid email provided", email=email)
                raise ValueError("Email must be a non-empty string")

            alerts = await self._repository.get_active_alerts_list_by_email(email=email)

            logger.info("Successfully retrieved alerts", email=email, alerts_count=len(alerts))
            return alerts

        except RepositoryError as e:
            logger.error(
                "Repository error while retrieving alerts",
                email=email,
                error=str(e),
                exc_info=True,
            )
            raise

        except ValueError as e:
            logger.error(
                "Validation error in GetAlertsUseCase",
                email=email,
                error=str(e),
                exc_info=True,
            )
            raise

        except Exception as e:
            logger.error(
                "Unexpected error in GetAlertsUseCase",
                email=email,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise
