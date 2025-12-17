import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import final

from ..enums.channel import ChannelEnum
from ..enums.status import StatusEnum
from ..exceptions import DomainValidationError


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
    message: str # в будущем VO
    recipient: str # в будущем VO
    source: str # в будущем VO
    status: StatusEnum
    sent_at: datetime
    created_at: datetime


    def __post_init__(self):
        if not isinstance(self.status, StatusEnum):
            raise DomainValidationError("Status must be a value from StatusEnum")
        if not isinstance(self.channel, ChannelEnum):
            raise DomainValidationError("Channel must be a value from ChannelEnum")
        if len(self.message) <= 0 or len(self.message) > 100:
            raise DomainValidationError("Message length must be between 1 and 100 characters")
        if len(self.recipient) <= 0 or len(self.recipient) > 100:
            raise DomainValidationError("Recipient length must be between 1 and 100 characters")

    def make_sent(self):
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



