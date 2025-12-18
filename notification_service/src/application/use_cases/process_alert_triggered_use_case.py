import structlog

from domain.enums.channel import ChannelEnum
from ...application.use_cases.send_email_notification import SendEmailNotificationUseCase
from ...application.use_cases.check_and_reserve import CheckAndReserveUseCase
from ...domain.exceptions import RepositoryError, EmailSendingError
from ...presentation.v1.schemas.alert_triggered import AlertTriggeredDTO

logger = structlog.getLogger(__name__)


class ProcessAlertTriggeredUseCase:
    """Use case for processing alert trigger events.

    This use case orchestrates the complete flow of processing an alert trigger:
    1. Checks and reserves notifications (creates notification entities)
    2. Sends email notifications for created entities

    Attributes:
        _check_and_reserve: Use case for checking and reserving notifications.
        _send_email: Use case for sending email notifications.
    """

    def __init__(
            self,
            check_and_reserve_use_case: CheckAndReserveUseCase,
            send_email_use_case: SendEmailNotificationUseCase,
    ):
        """Initialize the use case with required dependencies.

        Args:
            check_and_reserve_use_case: Use case for checking and reserving notifications.
            send_email_use_case: Use case for sending email notifications.
        """
        self._check_and_reserve = check_and_reserve_use_case
        self._send_email = send_email_use_case

    async def execute(self, dto_model: AlertTriggeredDTO) -> None:
        """Execute the alert trigger processing workflow.

        Processes an alert trigger event by creating notifications and sending
        them via email channel. Handles the complete flow from reservation to delivery.

        Args:
            dto_model: Alert trigger event data containing alert information,
                cryptocurrency details, and user contact information.

        Raises:
            RepositoryError: If database operation fails during notification
                creation or reservation.
            EmailSendingError: If email sending fails.
            Exception: For any other unexpected errors during processing.
        """
        try:
            logger.info(
                "Starting alert trigger processing",
                event_id=dto_model.id,
                email=dto_model.email,
                alert_id=dto_model.alert_id,
                cryptocurrency=dto_model.cryptocurrency
            )


            notifications = await self._check_and_reserve.execute(
                dto_model=dto_model,
            )

            if not notifications:
                logger.info(
                    "No notifications created for alert trigger",
                    event_id=dto_model.id,
                    email=dto_model.email,
                    alert_id=dto_model.alert_id
                )
                return

            logger.info(
                "Notifications created, starting email sending",
                event_id=dto_model.id,
                email=dto_model.email,
                notifications_count=len(notifications)
            )

            await self._send_email.execute(notifications)

            logger.info(
                "Alert trigger processing completed successfully",
                event_id=dto_model.id,
                email=dto_model.email,
                alert_id=dto_model.alert_id,
                created_at=dto_model.created_at
            )

        except RepositoryError as e:
            logger.error(
                "Repository error during alert trigger processing",
                event_id=dto_model.id,
                email=dto_model.email,
                alert_id=dto_model.alert_id,
                error=str(e),
                exc_info=True
            )
            raise

        except EmailSendingError as e:
            logger.error(
                "Email sending error during alert trigger processing",
                event_id=dto_model.id,
                email=dto_model.email,
                alert_id=dto_model.alert_id,
                error=str(e),
                exc_info=True
            )
            raise

        except Exception as e:
            logger.error(
                "Unexpected error during alert trigger processing",
                event_id=dto_model.id,
                email=dto_model.email,
                alert_id=dto_model.alert_id,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )
            raise
