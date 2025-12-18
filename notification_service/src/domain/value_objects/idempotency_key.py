from dataclasses import dataclass
from typing import final
from uuid import UUID

from ..exceptions import KeyValidationError
from domain.enums.channel import ChannelEnum


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class IdempotencyKeyVO:
    """
    Value Object for notification idempotency key.

    Ensures that the key is a string with length between 15 and 100 characters.
    Used to prevent notification duplication.
    """
    key: str

    def __post_init__(self):
        """
        Validate the idempotency key after initialization.

        Raises:
            KeyValidationError: If the key is not a string or has incorrect length.
        """
        if not isinstance(self.key, str):
            raise KeyValidationError("Key must be a string")
        if not (15 <= len(self.key) <= 100):
            raise KeyValidationError("Key length must be between 15 and 100 characters")

    @staticmethod
    def build(event_id: UUID | str, channel: ChannelEnum) -> "IdempotencyKeyVO":
        """
        Creates an idempotency key based on event ID and channel.

        Args:
            event_id: Unique event identifier (UUID or string).
            channel: Notification delivery channel.

        Returns:
            IdempotencyKeyVO: Instance with the generated key.
        """
        key = f"alert_triggered:{str(event_id)}:{str(channel.value)}"
        return IdempotencyKeyVO(key=key)