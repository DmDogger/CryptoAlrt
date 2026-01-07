import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import final

from ..enums.channel import ChannelEnum
from ..enums.status import StatusEnum
from ..exceptions import DomainValidationError
from ..value_objects.message import MessageValueObject
from ..value_objects.idempotency_key import IdempotencyKeyVO


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class NotificationEntity:
    """Domain entity representing a notification.

    Attributes:
        id: Unique identifier for the notification
        message: Notification message content (1-100 characters)
        recipient: Notification recipient identifier (1-100 characters)
        status: Current status of the notification
    """

    id: uuid.UUID
    channel: ChannelEnum
    message: MessageValueObject
    recipient: str  # в будущем VO
    idempotency_key: IdempotencyKeyVO
    status: StatusEnum
    sent_at: datetime | None
    created_at: datetime

    def __post_init__(self):
        if not isinstance(self.status, StatusEnum):
            raise DomainValidationError("Status must be a value from StatusEnum")
        if not isinstance(self.channel, ChannelEnum):
            raise DomainValidationError("Channel must be a value from ChannelEnum")
        if not isinstance(self.idempotency_key, IdempotencyKeyVO):
            raise DomainValidationError(
                "Idempotency key must be an IdempotencyKeyVO instance"
            )
        if len(self.message.text) < 5 or len(self.message.text) > 100:
            raise DomainValidationError(
                "Message length must be between 1 and 100 characters"
            )
        if len(self.recipient) < 5 or len(self.recipient) > 100:
            raise DomainValidationError(
                "Recipient length must be between 1 and 100 characters"
            )
        if self.sent_at:
            sent_at_naive = (
                self.sent_at.replace(tzinfo=None)
                if self.sent_at.tzinfo
                else self.sent_at
            )
            created_at_naive = (
                self.created_at.replace(tzinfo=None)
                if self.created_at.tzinfo
                else self.created_at
            )
            if sent_at_naive <= created_at_naive:
                raise DomainValidationError(
                    "Sent at date cannot be later than created_at"
                )

    @classmethod
    def create(
        cls,
        channel: ChannelEnum,
        message: MessageValueObject,
        recipient: str,
        idempotency_key: IdempotencyKeyVO,
    ):
        """Create a new notification entity.

        Args:
            channel: Notification delivery channel
            message: Notification message content (1-100 characters)
            recipient: Notification recipient identifier (1-100 characters)
            idempotency_key: Idempotency key to prevent duplicates

        Returns:
            NotificationEntity: A new instance with PENDING status,
            generated UUID, current UTC timestamp for created_at,
            and None for sent_at.
        """
        return cls(
            id=uuid.uuid4(),
            channel=channel,
            message=message,
            recipient=recipient,
            idempotency_key=idempotency_key,
            status=StatusEnum.PENDING,
            sent_at=None,
            created_at=datetime.now(UTC),
        )

    def make_sent(self) -> "NotificationEntity":
        """Mark notification as sent.

        Returns:
            NotificationEntity: A new instance with status set to SENT
            and sent_at timestamp set to current UTC time.
        """
        return NotificationEntity(
            id=self.id,
            channel=self.channel,
            message=self.message,
            recipient=self.recipient,
            idempotency_key=self.idempotency_key,
            status=StatusEnum.SENT,
            sent_at=datetime.now(UTC),
            created_at=self.created_at,
        )

    def mark_failed(self) -> "NotificationEntity":
        """Mark notification as failed.

        Returns:
            NotificationEntity: A new instance with status set to FAILED,
            preserving all other attributes including sent_at timestamp.
        """
        return NotificationEntity(
            id=self.id,
            channel=self.channel,
            message=self.message,
            recipient=self.recipient,
            idempotency_key=self.idempotency_key,
            status=StatusEnum.FAILED,
            sent_at=self.sent_at,
            created_at=self.created_at,
        )
