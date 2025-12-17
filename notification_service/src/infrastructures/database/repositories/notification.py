from dataclasses import dataclass
from typing import final
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import getLogger

from application.interfaces.repositories import NotificationRepositoryProtocol
from domain.entities.notification import NotificationEntity
from domain.exceptions import RepositoryError
from ..models.notification import Notification

logger = getLogger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class SQLAlchemyNotificationRepository(NotificationRepositoryProtocol):
    """SQLAlchemy implementation of the Alert Repository.

    This repository is responsible for database operations (CRUD) only.
    Mapping logic is delegated to AlertDBMapper following SRP.
    """
    session: AsyncSession
    _mapper: #TODO: сделаем маппер

    def __init__(
        self,
        session: AsyncSession,
        mapper,
    ) -> None:
        """
        Initialize the repository with database session and mapper.

        Args:
            session: The async SQLAlchemy session for database operations.
            mapper: The AlertDBMapper for converting between entities and database models.
        """
        object.__setattr__(self, 'session', session)
        object.__setattr__(self, '_mapper', mapper)

    async def get_notification_by_id(
        self, notification_id: str | UUID
    ) -> NotificationEntity | None:
        try:
            stmt = (
                select(Notification)
                .where(Notification.id == notification_id)
            )
            res = await self.session.scalars(stmt)
            result = res.first()
            if result is None:
                logger.error(f"[Error]: Alert with ID {alert_id} not found.")
                return None

            logger.info(f"[Info]: Retrieved alert with ID {alert_id}")
            return self._mapper.from_database_model(result)

        except SQLAlchemyError as e:
            logger.error(f"[SQLAlchemyError]: Unexpected error retrieving alert with ID {alert_id}: {e}")
            raise RepositoryError(f"Database error occurred while retrieving alert with ID: {alert_id}")
        except Exception as e:
            logger.error(f"[Unexpected error]: {e}")
            raise RepositoryError(f"Unexpected error occurred while retrieving alert with ID: {alert_id}")
