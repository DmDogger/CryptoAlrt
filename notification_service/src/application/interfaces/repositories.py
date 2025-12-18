from abc import abstractmethod
from typing import Protocol
from uuid import UUID

from domain.entities.notification import NotificationEntity
from domain.entities.user_preference import UserPreferenceEntity
from domain.enums.status import StatusEnum


class NotificationRepositoryProtocol(Protocol):
    """Protocol for a notification repository.
    
    Defines methods for retrieving and saving notification entities.
    """
    
    @abstractmethod
    async def get_by_id(
        self,
        notification_id: UUID
    ) -> NotificationEntity | None:
        """Get notification by its ID.
        
        Args:
            notification_id: Unique identifier of the notification.
            
        Returns:
            NotificationEntity if found, None otherwise.
        """
        ...
    
    @abstractmethod
    async def save(
        self,
        notification: NotificationEntity
    ) -> NotificationEntity:
        """Save a new notification entity.
        
        Args:
            notification: Notification entity to save.
            
        Returns:
            Saved notification entity.
        """
        ...
    
    @abstractmethod
    async def update(
        self,
        notification: NotificationEntity
    ) -> NotificationEntity:
        """Update an existing notification entity.
        
        Args:
            notification: Notification entity with updated data.
            
        Returns:
            Updated notification entity.
        """
        ...
    
    @abstractmethod
    async def get_by_status(
        self,
        status: StatusEnum
    ) -> list[NotificationEntity]:
        """Get all notifications with specified status.

        Args:
            status: Status to filter by.

        Returns:
            List of notification entities with the specified status.
        """
        ...

    @abstractmethod
    async def get_by_idempotency_key(
        self,
        idempotency_key: str
    ) -> NotificationEntity | None:
        """Get notification by its idempotency key.

        Args:
            idempotency_key: Idempotency key to search for.

        Returns:
            NotificationEntity if found, None otherwise.
        """
        ...


class PreferenceRepositoryProtocol(Protocol):
    """Protocol for a user preference repository.

    Defines methods for retrieving and saving user preference entities.
    """

    @abstractmethod
    async def get_by_id(
        self,
        preference_id: UUID
    ) -> UserPreferenceEntity | None:
        """Get user preference by its ID.

        Args:
            preference_id: Unique identifier of the user preference.

        Returns:
            UserPreferenceEntity if found, None otherwise.
        """
        ...

    @abstractmethod
    async def get_by_email(
        self,
        email: str
    ) -> UserPreferenceEntity | None:
        """Get user preference by email address.

        Args:
            email: User's email address.

        Returns:
            UserPreferenceEntity if found, None otherwise.
        """
        ...

    @abstractmethod
    async def get_by_telegram_id(
        self,
        telegram_id: int
    ) -> UserPreferenceEntity | None:
        """Get user preference by Telegram ID.

        Args:
            telegram_id: User's Telegram ID.

        Returns:
            UserPreferenceEntity if found, None otherwise.
        """
        ...

    @abstractmethod
    async def save(
        self,
        preference: UserPreferenceEntity
    ) -> UserPreferenceEntity:
        """Save a new user preference entity.

        Args:
            preference: User preference entity to save.

        Returns:
            Saved user preference entity.
        """
        ...

    @abstractmethod
    async def update(
        self,
        preference: UserPreferenceEntity
    ) -> UserPreferenceEntity:
        """Update an existing user preference entity.

        Args:
            preference: User preference entity with updated data.

        Returns:
            Updated user preference entity.
        """
        ...
