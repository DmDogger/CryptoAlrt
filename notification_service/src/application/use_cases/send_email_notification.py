import structlog

from domain.entities.notification import NotificationEntity
from domain.enums.channel import ChannelEnum
from domain.exceptions import EmailSendingError
from application.interfaces.repositories import NotificationRepositoryProtocol
from application.interfaces.email_client import EmailClientProtocol

logger = structlog.getLogger(__name__)


class SendEmailNotificationUseCase:
    """Use case for sending email notifications.

    This use case processes a list of notifications, filters for email channel
    notifications, sends emails via the email client, and updates notification
    status to SENT in the repository.

    Attributes:
        _email_client: Client for sending email messages.
        _repository: Repository for updating notification entities.
    """

    def __init__(
        self,
        email_client: EmailClientProtocol,
        repository: NotificationRepositoryProtocol,
    ):
        """Initialize the use case with required dependencies.

        Args:
            email_client: Client for sending email messages.
            repository: Repository for updating notification entities.
        """
        self._email_client = email_client
        self._repository = repository

    async def execute(
        self,
        notifications: list[NotificationEntity],
    ) -> None:
        """Execute email notification sending process.

        Processes a list of notifications, sending emails for EMAIL channel
        notifications and updating their status to SENT upon successful delivery.

        Args:
            notifications: List of notification entities to process. Only
                notifications with EMAIL channel will be processed.

        Raises:
            EmailSendingError: If email sending fails for any notification.
            RepositoryError: If updating notification status in repository fails.
            Exception: For any other unexpected errors during processing.

        Note:
            - Non-EMAIL channel notifications are skipped with a log message.
            - Each notification is processed independently; failures for one
              notification do not stop processing of others.
        """
        if not notifications:
            logger.warning("Notifications are empty")
            return

        for notification in notifications:
            if notification.channel == ChannelEnum.EMAIL:
                try:
                    logger.info(
                        "Processing email notification",
                        notification_id=str(notification.id),
                        recipient=notification.recipient,
                        status=notification.status.value,
                    )

                    await self._email_client.send(
                        to=notification.recipient,
                        from_="noreply@cryptoalrt.io",  # poka vremenno zdes
                        subject="Cryptocurrency Alert Notification",
                        body=notification.message.text,
                    )

                    updated_notification = notification.make_sent()
                    await self._repository.update(updated_notification)

                    logger.info(
                        "Email notification sent successfully",
                        notification_id=str(notification.id),
                        recipient=notification.recipient,
                    )

                except EmailSendingError as e:
                    logger.error(
                        "Failed to send email notification",
                        notification_id=str(notification.id),
                        recipient=notification.recipient,
                        error=str(e),
                        exc_info=True,
                    )
                    try:
                        failed_notification = notification.mark_failed()
                        await self._repository.update(failed_notification)
                    except Exception:
                        logger.error(
                            "Failed to mark notification as FAILED after email error",
                            notification_id=str(notification.id),
                            exc_info=True,
                        )
                    continue

                except Exception as e:
                    logger.error(
                        "Unexpected error during email notification processing",
                        notification_id=str(notification.id),
                        recipient=notification.recipient,
                        error=str(e),
                        error_type=type(e).__name__,
                        exc_info=True,
                    )
                    try:
                        failed_notification = notification.mark_failed()
                        await self._repository.update(failed_notification)
                    except Exception:
                        logger.error(
                            "Failed to mark notification as FAILED after unexpected error",
                            notification_id=str(notification.id),
                            exc_info=True,
                        )
                    continue
