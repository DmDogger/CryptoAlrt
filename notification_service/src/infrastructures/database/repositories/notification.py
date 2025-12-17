from dataclasses import dataclass
from typing import final
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import getLogger

from application.interfaces.repositories import NotificationRepositoryProtocol
from domain.entities.notification import NotificationEntity
from domain.enums.status import StatusEnum
from domain.exceptions import RepositoryError
from ..mappers.notification_db_mapper import NotificationDBMapper
from ..models.notification import Notification

logger = getLogger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class SQLAlchemyNotificationRepository(NotificationRepositoryProtocol):
    """SQLAlchemy implementation of the Notification Repository.

    This repository is responsible for database operations (CRUD) only.
    Mapping logic is delegated to NotificationDBMapper following SRP.
    """
    session: AsyncSession
    _mapper: NotificationDBMapper

    def __init__(
        self,
        session: AsyncSession,
        mapper: NotificationDBMapper,
    ) -> None:
        """
        Initialize the repository with database session and mapper.

        Args:
            session: The async SQLAlchemy session for database operations.
            mapper: The NotificationDBMapper for converting between entities and database models.
        """
        object.__setattr__(self, 'session', session)
        object.__setattr__(self, '_mapper', mapper)

    async def get_by_id(
        self, notification_id: UUID
    ) -> NotificationEntity | None:
        """
        Get notification by its ID.

        Args:
            notification_id: Unique identifier of the notification.

        Returns:
            NotificationEntity if found, None otherwise.
        """
        try:
            logger.info("Retrieving notification", notification_id=str(notification_id))

            stmt = (
                select(Notification)
                .where(Notification.id == notification_id)
            )
            res = await self.session.scalars(stmt)
            result = res.first()

            if result is None:
                logger.warning("Notification not found", notification_id=str(notification_id))
                return None

            logger.info("Notification retrieved successfully", notification_id=str(notification_id))
            return self._mapper.from_database_model(result)

        except SQLAlchemyError as e:
            logger.error(
                "SQLAlchemy error during notification retrieval",
                notification_id=str(notification_id),
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Database error occurred while retrieving notification with ID: {notification_id}")
        except Exception as e:
            logger.error(
                "Unexpected error during notification retrieval",
                notification_id=str(notification_id),
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Unexpected error occurred while retrieving notification with ID: {notification_id}")

    async def save(self, entity: NotificationEntity) -> NotificationEntity:
        """
        Save a new notification entity.

        Args:
            entity: Notification entity to save.

        Returns:
            Saved notification entity.

        Raises:
            RepositoryError: If database operation fails.
        """
        try:
            logger.info(
                "Saving notification",
                notification_id=str(entity.id),
                status=entity.status.value,
                channel=entity.channel.value
            )

            db_model = self._mapper.to_database_model(entity)
            self.session.add(db_model)
            await self.session.commit()

            logger.info(
                "Notification saved successfully",
                notification_id=str(entity.id)
            )
            return entity

        except IntegrityError as e:
            await self.session.rollback()
            logger.error(
                "Integrity error during notification save",
                notification_id=str(entity.id),
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Notification with this data already exists or constraint violated: {entity.id}") from e
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(
                "SQLAlchemy error during notification save",
                notification_id=str(entity.id),
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Database error occurred while saving notification with ID: {entity.id}") from e
        except Exception as e:
            await self.session.rollback()
            logger.error(
                "Unexpected error during notification save",
                notification_id=str(entity.id),
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Unexpected error occurred while saving notification with ID: {entity.id}") from e

    async def update(self, notification_id: UUID, entity: NotificationEntity) -> NotificationEntity:
        """
        Update an existing notification entity.

        Args:
            notification_id: Unique identifier of the notification to update.
            entity: Notification entity with updated data.

        Returns:
            Updated notification entity.

        Raises:
            RepositoryError: If database operation fails.
        """
        try:
            logger.info(
                "Updating notification",
                notification_id=str(entity.id),
                status=entity.status.value
            )

            dict_model = self._mapper.to_dict(entity)

            upd_stmt = (
                update(Notification)
                .where(Notification.id == notification_id)
                .values(dict_model)
                .returning(Notification)
            )

            entity = await self.session.execute(upd_stmt)

            logger.info(
                "Notification updated successfully",
                notification_id=str(entity.id)
            )
            return entity

        except IntegrityError as e:
            await self.session.rollback()
            logger.error(
                "Integrity error during notification update",
                notification_id=str(entity.id),
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Notification update violates constraints: {entity.id}") from e
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(
                "SQLAlchemy error during notification update",
                notification_id=str(entity.id),
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Database error occurred while updating notification with ID: {entity.id}") from e
        except Exception as e:
            await self.session.rollback()
            logger.error(
                "Unexpected error during notification update",
                notification_id=str(entity.id),
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Unexpected error occurred while updating notification with ID: {entity.id}") from e

    async def get_by_status(self, status: StatusEnum) -> list[NotificationEntity]:
        """
        Get all notifications with specified status.

        Args:
            status: Status to filter by.

        Returns:
            List of notification entities with the specified status.
        """
        try:
            logger.info("Retrieving notifications by status", status=status.value)

            stmt = (
                select(Notification)
                .where(Notification.status == status.value)
            )
            res = await self.session.scalars(stmt)
            results = res.all()

            entities = [self._mapper.from_database_model(result) for result in results]

            logger.info(
                "Notifications retrieved by status",
                status=status.value,
                count=len(entities)
            )
            return entities

        except SQLAlchemyError as e:
            logger.error(
                "SQLAlchemy error during notifications retrieval by status",
                status=status.value,
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Database error occurred while retrieving notifications with status: {status.value}")
        except Exception as e:
            logger.error(
                "Unexpected error during notifications retrieval by status",
                status=status.value,
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Unexpected error occurred while retrieving notifications with status: {status.value}")

