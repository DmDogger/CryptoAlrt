from dataclasses import dataclass
from typing import final
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import getLogger

from src.application.interfaces.repositories import AlertRepositoryProtocol
from src.domain.entities.alert import AlertEntity
from src.domain.exceptions import RepositoryError
from src.infrastructures.database.mappers.alert_db_mapper import AlertDBMapper
from src.infrastructures.database.mappers.cryptocurrency_db_mapper import CryptocurrencyDBMapper
from src.infrastructures.database.models.alert import Alert

logger = getLogger(__name__)

@final
@dataclass(frozen=True, slots=True, kw_only=True)
class SQLAlchemyAlertRepository(AlertRepositoryProtocol):
    """SQLAlchemy implementation of the Alert Repository.

    This repository is responsible for database operations (CRUD) only.
    Mapping logic is delegated to AlertDBMapper following SRP.
    """
    session: AsyncSession
    _mapper: AlertDBMapper

    def __init__(
        self,
        session: AsyncSession,
        mapper: AlertDBMapper,
    ) -> None:
        """
        Initialize the repository with database session and mapper.

        Args:
            session: The async SQLAlchemy session for database operations.
            mapper: The AlertDBMapper for converting between entities and database models.
        """
        object.__setattr__(self, 'session', session)
        object.__setattr__(self, '_mapper', mapper)

    async def get_alert_by_id(
        self, alert_id: str | UUID
    ) -> AlertEntity | None:
        try:
            stmt = (
                select(Alert)
                .options(joinedload(Alert.cryptocurrency))
                .where(Alert.id == alert_id)
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

    async def save(self, cryptocurrency_id: UUID, alert: AlertEntity) -> None:
        try:
            model = self._mapper.to_database_model(
                entity=alert,
                cryptocurrency_id=cryptocurrency_id
            )
            self.session.add(model)
            await self.session.commit()
            logger.info(f"[Info]: Alert with ID {alert.id} saved successfully")

        except IntegrityError as e:
            logger.error(f"[IntegrityError]: Integrity error saving alert with ID {alert.id}: {e}")
            await self.session.rollback()
            raise RepositoryError(f"Integrity error occurred while saving alert with ID: {alert.id}")

        except SQLAlchemyError as e:
            logger.error(f"[SQLAlchemyError]: Database error saving alert with ID {alert.id}: {e}")
            await self.session.rollback()
            raise RepositoryError(f"Database error occurred while saving alert with ID: {alert.id}")

        except Exception as e:
            logger.error(f"[Unexpected error]: {e}")
            await self.session.rollback()
            raise RepositoryError(f"Unexpected error occurred while saving alert with ID: {alert.id}")





