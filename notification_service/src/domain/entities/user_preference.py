import uuid
from dataclasses import field, dataclass
from typing import final

from domain.exceptions import DomainValidationError


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class UserPreferenceEntity:
    """Domain entity representing user notification preferences.
    
    This immutable entity stores user preferences for receiving notifications
    via different channels (email and telegram).
    
    Attributes:
        id: Unique identifier for the user preference.
        email: User's email address.
        email_enabled: Whether email notifications are enabled (default: True).
        telegram_id: User's Telegram ID if available (default: None).
        telegram_enabled: Whether Telegram notifications are enabled (default: False).
    """
    id: uuid.UUID
    email: str
    email_enabled: bool = field(default=True)
    telegram_id: int | None = None
    telegram_enabled: bool = field(default=False)

    def __post_init__(self):
        if len(self.email) < 5 or len(self.email) > 100:
            raise DomainValidationError("Email length must be between 5 and 100 characters")

    @classmethod
    def create(
            cls,
            email: str,
            email_enabled: bool = True,
            telegram_id: int | None = None,
            telegram_enabled: bool | None = None,
    ) -> "UserPreferenceEntity":
        """Create a new user preference entity.
        
        Args:
            email: User's email address.
            email_enabled: Whether email notifications are enabled (default: True).
            telegram_id: User's Telegram ID if available (default: None).
            telegram_enabled: Whether Telegram notifications are enabled.
                If None, defaults to False (default: None).
            
        Returns:
            UserPreferenceEntity: A new instance with generated UUID and specified preferences.
        """
        return cls(
            id=uuid.uuid4(),
            email=email,
            email_enabled=email_enabled,
            telegram_enabled=telegram_enabled if telegram_enabled is not None else False,
            telegram_id=telegram_id,
        )

    def set_email_enabled(self) -> "UserPreferenceEntity":
        """Enable email notifications.
        
        Returns:
            UserPreferenceEntity: A new instance with email_enabled set to True,
            preserving all other attributes.
        """
        return UserPreferenceEntity(
            id=self.id,
            email=self.email,
            email_enabled=True,
            telegram_id=self.telegram_id,
            telegram_enabled=self.telegram_enabled,
        )

    def set_email_disable(self) -> "UserPreferenceEntity":
        """Disable email notifications.
        
        Returns:
            UserPreferenceEntity: A new instance with email_enabled set to False,
            preserving all other attributes.
        """
        return UserPreferenceEntity(
            id=self.id,
            email=self.email,
            email_enabled=False,
            telegram_id=self.telegram_id,
            telegram_enabled=self.telegram_enabled,
        )

    def set_telegram_enabled(self) -> "UserPreferenceEntity":
        """Enable Telegram notifications.
        
        Returns:
            UserPreferenceEntity: A new instance with telegram_enabled set to True,
            preserving all other attributes.
        """
        return UserPreferenceEntity(
            id=self.id,
            email=self.email,
            email_enabled=self.email_enabled,
            telegram_id=self.telegram_id,
            telegram_enabled=True,
        )

    def set_telegram_disable(self) -> "UserPreferenceEntity":
        """Disable Telegram notifications.
        
        Returns:
            UserPreferenceEntity: A new instance with telegram_enabled set to False,
            preserving all other attributes.
        """
        return UserPreferenceEntity(
            id=self.id,
            email=self.email,
            email_enabled=self.email_enabled,
            telegram_id=self.telegram_id,
            telegram_enabled=False,
        )





