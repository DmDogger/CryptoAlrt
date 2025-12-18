import structlog

from domain.entities.notification import NotificationEntity
from domain.value_objects.message import MessageValueObject
from application.interfaces.repositories import (
    PreferenceRepositoryProtocol,
    NotificationRepositoryProtocol,
)
from domain.enums.channel import ChannelEnum
from domain.value_objects.idempotency_key import IdempotencyKeyVO
from domain.exceptions import RepositoryError
from domain.events.alert_triggered import AlertTriggeredEvent

logger = structlog.getLogger(__name__)


class CheckAndReserveUseCase:
    """Use case for checking and reserving notifications for alert triggers.

    This use case handles the creation of notifications when an alert threshold
    is triggered. It checks user preferences, validates idempotency, and creates
    notifications for enabled channels (email and/or telegram).

    Attributes:
        _notification_repository: Repository for managing notification entities.
        _preference_repository: Repository for accessing user preferences.
    """

    def __init__(
            self,
            notification_repository: NotificationRepositoryProtocol,
            preference_repository: PreferenceRepositoryProtocol,
    ):
        """Initialize the use case with required repositories.

        Args:
            notification_repository: Repository for managing notification entities.
            preference_repository: Repository for accessing user preferences.
        """
        self._notification_repository = notification_repository
        self._preference_repository = preference_repository

    async def execute(
            self,
            event: AlertTriggeredEvent,
    ) -> list[NotificationEntity] | None:
        """Execute the check and reserve process for alert trigger notifications.

        This method processes an alert trigger event by:
        1. Retrieving user preferences for the alert owner
        2. Checking if notifications already exist (idempotency check)
        3. Creating notifications for enabled channels (email and/or telegram)
        4. Ensuring no duplicate notifications are created

        Args:
            event: Alert trigger event data containing alert information,
                cryptocurrency details, and user contact information.
                for the same event.

        Returns:
            List of created NotificationEntity instances if notifications were
            successfully created, None if:
            - User preferences not found
            - All notification channels are disabled
            - Notification with idempotency key already exists
            - No notifications were created

        Raises:
            RepositoryError: If database operation fails during preference
                retrieval or notification creation.
            Exception: For any other unexpected errors during processing.
        """
        try:
            logger.info(
                "Starting check and reserve process",
                event_id=event.id,
                email=event.email,
                alert_id=event.alert_id
            )

            user_preference = await self._preference_repository.get_by_email(event.email)

            if not user_preference:
                logger.warning(
                    "User preference not found",
                    email=event.email,
                    event_id=event.id
                )
                return None

            if not user_preference.email_enabled and not user_preference.telegram_enabled:
                logger.info(
                    "All notification channels disabled for user",
                    email=event.email,
                    event_id=event.id
                )
                return None

            entities_list = []

            if user_preference.email_enabled and user_preference.email:
                logger.info(
                    "Processing email notification",
                    email=user_preference.email,
                    event_id=event.id
                )

                idempotency_key_for_email = IdempotencyKeyVO.build(
                    event_id=event.id,
                    channel=ChannelEnum.EMAIL,
                )

                if await self._notification_repository.get_by_idempotency_key(idempotency_key_for_email.key):
                    logger.warning(
                        "Email notification already exists",
                        idempotency_key=idempotency_key_for_email.key,
                        event_id=event.id
                    )
                    return None

                notification = NotificationEntity.create(
                    channel=ChannelEnum.EMAIL,
                    message=MessageValueObject(
                        text=f"Threshold notification: {event.cryptocurrency} reached {event.current_price}"
                    ),
                    recipient=user_preference.email,
                    idempotency_key=idempotency_key_for_email
                )

                entity = await self._notification_repository.save(notification)
                entities_list.append(entity)

                logger.info(
                    "Email notification created successfully",
                    notification_id=str(entity.id),
                    email=user_preference.email,
                    event_id=event.id
                )

            if user_preference.telegram_enabled and user_preference.telegram_id:
                logger.info(
                    "Processing telegram notification",
                    telegram_id=user_preference.telegram_id,
                    event_id=event.id
                )

                idempotency_key_for_telegram = IdempotencyKeyVO.build(
                    event_id=event.id,
                    channel=ChannelEnum.TELEGRAM
                )

                if await self._notification_repository.get_by_idempotency_key(idempotency_key_for_telegram.key):
                    logger.warning(
                        "Telegram notification already exists",
                        idempotency_key=idempotency_key_for_telegram.key,
                        event_id=event.id
                    )
                    return None

                notification = NotificationEntity.create(
                    channel=ChannelEnum.TELEGRAM,
                    message=MessageValueObject(
                        text=f"Threshold notification: {event.cryptocurrency} reached {event.current_price}"
                    ),
                    recipient=str(user_preference.telegram_id),
                    idempotency_key=idempotency_key_for_telegram
                )

                entity = await self._notification_repository.save(notification)
                entities_list.append(entity)

                logger.info(
                    "Telegram notification created successfully",
                    notification_id=str(entity.id),
                    telegram_id=user_preference.telegram_id,
                    event_id=event.id
                )

            logger.info(
                "Check and reserve process completed",
                event_id=event.id,
                notifications_created=len(entities_list)
            )

            return entities_list if entities_list else None

        except RepositoryError as e:
            logger.error(
                "Repository error during check and reserve",
                event_id=event.id,
                email=event.email,
                error=str(e),
                exc_info=True
            )
            raise

        except Exception as e:
            logger.error(
                "Unexpected error during check and reserve",
                event_id=event.id,
                email=event.email,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )
            raise

















