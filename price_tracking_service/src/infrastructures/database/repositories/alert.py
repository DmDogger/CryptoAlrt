import uuid
from dataclasses import dataclass
from typing import final
from uuid import UUID

from sqlalchemy import select, desc, update, delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import getLogger

from application.interfaces.repositories import AlertRepositoryProtocol
from domain.entities.alert import AlertEntity
from domain.exceptions import RepositoryError
from infrastructures.database.mappers.alert_db_mapper import AlertDBMapper
from infrastructures.database.mappers.cryptocurrency_db_mapper import CryptocurrencyDBMapper
from infrastructures.database.models.alert import Alert

from infrastructures.database.models.cryptocurrency import Cryptocurrency

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

    async def get_active_alerts_by_name(self, crypto_name: str) -> list[AlertEntity]:
        """Retrieve all active alerts for a specific cryptocurrency name.

        Args:
            crypto_name: Cryptocurrency name to filter alerts (e.g., Bitcoin, Ethereum).

        Returns:
            List of active AlertEntity objects, empty list if none found.

        Raises:
            RepositoryError: If a database error occurs during retrieval.
        """
        try:
            logger.info(f"Retrieving active alerts for cryptocurrency name: {crypto_name}")

            stmt = (
                select(Alert)
                .join(Alert.cryptocurrency)
                .where(
                    Cryptocurrency.name == crypto_name,
                    Alert.is_active == True
                )
                .order_by(desc(Alert.created_at))
            )
            result = await self.session.scalars(stmt)
            alerts = result.all()

            if not alerts:
                logger.info(f"No active alerts found for cryptocurrency name: {crypto_name}")
                return []

            logger.info(f"Retrieved {len(alerts)} active alert(s) for cryptocurrency name: {crypto_name}")
            return [self._mapper.from_database_model(alert) for alert in alerts]

        except SQLAlchemyError as e:
            logger.error(f"[SQLAlchemyError]: Database error retrieving active alerts for cryptocurrency name {name}: {e}")
            raise RepositoryError(f"Database error occurred while retrieving active alerts for cryptocurrency name: {name}")

        except Exception as e:
            logger.error(f"[Unexpected error]: Unexpected error retrieving active alerts for cryptocurrency name {name}: {e}")
            raise RepositoryError(f"Unexpected error occurred while retrieving active alerts for cryptocurrency name: {name}")

    async def get_active_alerts_list_by_email(self, email: str) -> list[AlertEntity]:
        """Retrieve all active alerts for a specific email.

        Args:
            email: User's email address to filter alerts.

        Returns:
            List of active AlertEntity objects, empty list if none found.

        Raises:
            RepositoryError: If a database error occurs during retrieval.
        """
        try:
            logger.info(f"Retrieving active alerts for email: {email}")

            stmt = (
                select(Alert)
                .where(Alert.email == email,
                       Alert.is_active == True)
                .options(selectinload(Alert.cryptocurrency))
                .order_by(desc(Alert.created_at))
            )
            logger.info(f"Executing query: {stmt}")
            result = await self.session.scalars(stmt)
            alerts = result.all()
            logger.info(f"Query executed, found {len(alerts)} alerts")

            if not alerts:
                logger.info(f"No active alerts found for email: {email}")
                return []

            logger.info(f"Retrieved {len(alerts)} active alert(s) for email: {email}")
            return [self._mapper.from_database_model(alert) for alert in alerts]

        except SQLAlchemyError as e:
            logger.error(f"[SQLAlchemyError]: Database error retrieving active alerts for email {email}: {e}")
            raise RepositoryError(f"Database error occurred while retrieving active alerts for email: {email}")
        
        except Exception as e:
            logger.error(f"[Unexpected error]: Unexpected error retrieving active alerts for email {email}: {e}")
            raise RepositoryError(f"Unexpected error occurred while retrieving active alerts for email: {email}")

    async def get_active_alerts_list(self) -> list[AlertEntity]:
        """Retrieve all active alerts from the database.
        
        Returns:
            List of all active AlertEntity objects, empty list if none found.
            
        Raises:
            RepositoryError: If a database error occurs during retrieval.
        """
        try:
            logger.info("Retrieving all active alerts")
            stmt = (
                select(Alert)
                .where(Alert.is_active == True)
                .order_by(desc(Alert.created_at))
            )
            result = await self.session.scalars(stmt)
            alerts = result.all()

            if not alerts:
                logger.info("No active alerts found in the database")
                return []

            logger.info(f"Retrieved {len(alerts)} active alert(s) from the database")
            return [self._mapper.from_database_model(alert) for alert in alerts]

        except SQLAlchemyError as e:
            logger.error(f"[SQLAlchemyError]: Database error retrieving all active alerts: {e}")
            raise RepositoryError("Database error occurred while retrieving all active alerts")
        
        except Exception as e:
            logger.error(f"[Unexpected error]: Unexpected error retrieving all active alerts: {e}")
            raise RepositoryError("Unexpected error occurred while retrieving all active alerts")


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


    async def update(self, alert: AlertEntity) -> AlertEntity:
        try:
            model_dict = self._mapper.to_dict(alert)
            stmt = (
                update(Alert)
                .where(Alert.id == alert.id)
                .values(model_dict)
                .returning(Alert)
            )
            result = await self.session.execute(stmt)
            updated_model = result.scalar_one()
            await self.session.commit()
            logger.info(f"[Info]: Alert with ID {alert.id} updated successfully")
            return self._mapper.from_database_model(updated_model)

        except SQLAlchemyError as e:
            logger.error(f"[SQLAlchemyError]: Database error updating alert with ID {alert.id}: {e}")
            await self.session.rollback()
            raise RepositoryError(f"Database error occurred while updating alert with ID: {alert.id}")

        except Exception as e:
            logger.error(f"[Unexpected error]: {e}")
            await self.session.rollback()
            raise RepositoryError(f"Unexpected error occurred while updating alert with ID: {alert.id}")

    async def get_active_alerts_by_name(self, crypto_name: str) -> list[AlertEntity]:
        """Retrieve all active alerts for a specific cryptocurrency by name.

        Args:
            crypto_name: Name of the cryptocurrency (e.g., "Bitcoin", "BTC").

        Returns:
            List of active AlertEntity objects for the cryptocurrency.

        Raises:
            RepositoryError: If database error occurs.
        """
        try:
            logger.info(f"Retrieving active alerts for cryptocurrency: {crypto_name}")

            # Join with cryptocurrency table to filter by name and load related data
            stmt = (
                select(Alert)
                .options(selectinload(Alert.cryptocurrency))  # Load cryptocurrency data
                .join(Cryptocurrency, Alert.cryptocurrency_id == Cryptocurrency.id)
                .where(
                    Cryptocurrency.symbol == crypto_name,
                    Alert.is_active == True
                )
            )

            result = await self.session.execute(stmt)
            alerts = result.scalars().all()

            logger.info(f"Query executed, found {len(alerts)} alerts for {crypto_name}")

            if not alerts:
                logger.info(f"No active alerts found for cryptocurrency: {crypto_name}")
                return []

            logger.info(f"Retrieved {len(alerts)} active alert(s) for cryptocurrency: {crypto_name}")
            return [self._mapper.from_database_model(alert) for alert in alerts]

        except SQLAlchemyError as e:
            logger.error(f"[SQLAlchemyError]: Database error retrieving active alerts for cryptocurrency {crypto_name}: {e}")
            raise RepositoryError(f"Database error occurred while retrieving active alerts for cryptocurrency: {crypto_name}")

        except Exception as e:
            logger.error(f"[Unexpected error]: Unexpected error retrieving active alerts for cryptocurrency {crypto_name}: {e}")
            raise RepositoryError(f"Unexpected error occurred while retrieving active alerts for cryptocurrency: {crypto_name}")

    async def delete_alert_by_id(self, email: str, alert_id: uuid.UUID):
        """Delete alert by id scoped to a user email."""
        try:

            logger.info(f"Starting to delete alert for {email} with alert id: {alert_id}...")
            stmt = (
                delete(Alert)
                .where(Alert.email == email,
                       Alert.id == alert_id)
            )
            await self.session.execute(stmt)
            await self.session.commit()
            logger.info(f"Succeed deleting alert for {email}")

        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(
                f"[SQLAlchemyError]: Database error during deleting alert with for {email} with alert id: {alert_id}: {e}")
            raise RepositoryError(
                f"Database error during deleting alert with for {email} with alert id: {alert_id}: {e}")

        except Exception as e:
            logger.error(
                f"[Unexpected error]: Unexpected error during deleting alert with for {email} with alert id: {alert_id}: {e}")
            raise RepositoryError(
                f"Unexpected Database error during deleting alert with for {email} with alert id: {alert_id}: {e}")








