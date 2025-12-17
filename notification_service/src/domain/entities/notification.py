import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import final

from ..enums.channel import ChannelEnum
from ..enums.status import StatusEnum
from ..exceptions import DomainValidationError
from ..value_objects.message import MessageValueObject


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class NotificationEntity:
    """Domain entity representing a notification.
    
    Attributes:
        id: Unique identifier for the notification
        message: Notification message content (1-100 characters)
        recipient: Notification recipient identifier (1-100 characters)
        source: Notification source identifier
        status: Current status of the notification
    """
    id: uuid.UUID
    channel: ChannelEnum
    message: MessageValueObject
    recipient: str # в будущем VO
    source: str # в будущем VO
    status: StatusEnum
    sent_at: datetime | None
    created_at: datetime


    def __post_init__(self):
        if not isinstance(self.status, StatusEnum):
            raise DomainValidationError("Status must be a value from StatusEnum")
        if not isinstance(self.channel, ChannelEnum):
            raise DomainValidationError("Channel must be a value from ChannelEnum")
        if len(self.message.text) <= 0 or len(self.message.text) > 100:
            raise DomainValidationError("Message length must be between 1 and 100 characters")
        if len(self.recipient) <= 0 or len(self.recipient) > 100:
            raise DomainValidationError("Recipient length must be between 1 and 100 characters")
        if self.sent_at > self.created_at:
            raise DomainValidationError("Sent at date cannot be later than created_at")

    @classmethod
    def create(
            cls,
            channel: ChannelEnum,
            message: MessageValueObject,
            recipient: str,
            source: str,
    ):
        """Create a new notification entity.
        
        Args:
            channel: Notification delivery channel
            message: Notification message content (1-100 characters)
            recipient: Notification recipient identifier (1-100 characters)
            source: Notification source identifier
            
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
            source=source,
            status=StatusEnum.PENDING,
            sent_at=None,
            created_at=datetime.now(UTC)
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
            source=self.source,
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
            source=self.source,
            status=StatusEnum.FAILED,
            sent_at=self.sent_at,
            created_at=self.created_at,
        )


