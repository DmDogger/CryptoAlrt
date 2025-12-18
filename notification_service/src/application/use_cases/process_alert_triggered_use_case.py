import structlog

from application.use_cases.send_email_notification import SendEmailNotificationUseCase
from application.use_cases.check_and_reserve import CheckAndReserveUseCase
from domain.exceptions import RepositoryError, EmailSendingError
from domain.events.alert_triggered import AlertTriggeredEvent

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

    async def execute(self, event: AlertTriggeredEvent) -> None:
        """Execute the alert trigger processing workflow.

        Processes an alert trigger event by creating notifications and sending
        them via email channel. Handles the complete flow from reservation to delivery.

        Args:
            event: Alert trigger event data containing alert information,
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
                event_id=event.id,
                email=event.email,
                alert_id=event.alert_id,
                cryptocurrency=event.cryptocurrency
            )


            notifications = await self._check_and_reserve.execute(
                event=event,
            )

            if not notifications:
                logger.info(
                    "No notifications created for alert trigger",
                    event_id=event.id,
                    email=event.email,
                    alert_id=event.alert_id
                )
                return

            logger.info(
                "Notifications created, starting email sending",
                event_id=event.id,
                email=event.email,
                notifications_count=len(notifications)
            )

            await self._send_email.execute(notifications)

            logger.info(
                "Alert trigger processing completed successfully",
                event_id=event.id,
                email=event.email,
                alert_id=event.alert_id,
                created_at=event.created_at
            )

        except RepositoryError as e:
            logger.error(
                "Repository error during alert trigger processing",
                event_id=event.id,
                email=event.email,
                alert_id=event.alert_id,
                error=str(e),
                exc_info=True
            )
            raise

        except EmailSendingError as e:
            logger.error(
                "Email sending error during alert trigger processing",
                event_id=event.id,
                email=event.email,
                alert_id=event.alert_id,
                error=str(e),
                exc_info=True
            )
            raise

        except Exception as e:
            logger.error(
                "Unexpected error during alert trigger processing",
                event_id=event.id,
                email=event.email,
                alert_id=event.alert_id,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )
            raise
