from abc import abstractmethod
from typing import Protocol
from uuid import UUID

from domain.entities.notification import NotificationEntity
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
