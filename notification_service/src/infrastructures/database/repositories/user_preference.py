


from dataclasses import dataclass
from typing import final
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import getLogger

from application.interfaces.repositories import PreferenceRepositoryProtocol
from domain.entities.user_preference import UserPreferenceEntity
from domain.exceptions import RepositoryError
from ..mappers.user_preference_db_mapper import UserPreferenceDBMapper
from ..models.user_preference import UserPreference

logger = getLogger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class SQLAlchemyUserPreferenceRepository(PreferenceRepositoryProtocol):
    """SQLAlchemy implementation of the User Preference Repository.

    This repository is responsible for database operations (CRUD) only.
    Mapping logic is delegated to UserPreferenceDBMapper following SRP.
    """
    session: AsyncSession
    _mapper: UserPreferenceDBMapper

    def __init__(
        self,
        session: AsyncSession,
        mapper: UserPreferenceDBMapper,
    ) -> None:
        """
        Initialize the repository with database session and mapper.

        Args:
            session: The async SQLAlchemy session for database operations.
            mapper: The UserPreferenceDBMapper for converting between entities and database models.
        """
        object.__setattr__(self, 'session', session)
        object.__setattr__(self, '_mapper', mapper)

    async def get_by_id(
        self, preference_id: UUID
    ) -> UserPreferenceEntity | None:
        """
        Get user preference by its ID.

        Args:
            preference_id: Unique identifier of the user preference.

        Returns:
            UserPreferenceEntity if found, None otherwise.
        """
        try:
            logger.info("Retrieving user preference", preference_id=str(preference_id))

            stmt = (
                select(UserPreference)
                .where(UserPreference.id == preference_id)
            )
            res = await self.session.scalars(stmt)
            result = res.first()

            if result is None:
                logger.warning("User preference not found", preference_id=str(preference_id))
                return None

            logger.info("User preference retrieved successfully", preference_id=str(preference_id))
            return self._mapper.from_database_model(result)

        except SQLAlchemyError as e:
            logger.error(
                "SQLAlchemy error during user preference retrieval",
                preference_id=str(preference_id),
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Database error occurred while retrieving user preference with ID: {preference_id}")
        except Exception as e:
            logger.error(
                "Unexpected error during user preference retrieval",
                preference_id=str(preference_id),
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Unexpected error occurred while retrieving user preference with ID: {preference_id}")

    async def get_by_email(
        self, email: str
    ) -> UserPreferenceEntity | None:
        """
        Get user preference by email address.

        Args:
            email: User's email address.

        Returns:
            UserPreferenceEntity if found, None otherwise.
        """
        try:
            logger.info("Retrieving user preference by email", email=email)

            stmt = (
                select(UserPreference)
                .where(UserPreference.email == email)
            )
            res = await self.session.scalars(stmt)
            result = res.first()

            if result is None:
                logger.warning("User preference not found by email", email=email)
                return None

            logger.info("User preference retrieved successfully by email", email=email)
            return self._mapper.from_database_model(result)

        except SQLAlchemyError as e:
            logger.error(
                "SQLAlchemy error during user preference retrieval by email",
                email=email,
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Database error occurred while retrieving user preference by email: {email}")
        except Exception as e:
            logger.error(
                "Unexpected error during user preference retrieval by email",
                email=email,
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Unexpected error occurred while retrieving user preference by email: {email}")

    async def get_by_telegram_id(
        self, telegram_id: int
    ) -> UserPreferenceEntity | None:
        """
        Get user preference by Telegram ID.

        Args:
            telegram_id: User's Telegram ID.

        Returns:
            UserPreferenceEntity if found, None otherwise.
        """
        try:
            logger.info("Retrieving user preference by telegram_id", telegram_id=telegram_id)

            stmt = (
                select(UserPreference)
                .where(UserPreference.telegram_id == telegram_id)
            )
            res = await self.session.scalars(stmt)
            result = res.first()

            if result is None:
                logger.warning("User preference not found by telegram_id", telegram_id=telegram_id)
                return None

            logger.info("User preference retrieved successfully by telegram_id", telegram_id=telegram_id)
            return self._mapper.from_database_model(result)

        except SQLAlchemyError as e:
            logger.error(
                "SQLAlchemy error during user preference retrieval by telegram_id",
                telegram_id=telegram_id,
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Database error occurred while retrieving user preference by telegram_id: {telegram_id}")
        except Exception as e:
            logger.error(
                "Unexpected error during user preference retrieval by telegram_id",
                telegram_id=telegram_id,
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Unexpected error occurred while retrieving user preference by telegram_id: {telegram_id}")

    async def save(self, preference: UserPreferenceEntity) -> UserPreferenceEntity:
        """
        Save a new user preference entity.

        Args:
            preference: User preference entity to save.

        Returns:
            Saved user preference entity.

        Raises:
            RepositoryError: If database operation fails.
        """
        try:
            logger.info(
                "Saving user preference",
                preference_id=str(preference.id),
                email=preference.email,
                email_enabled=preference.email_enabled,
                telegram_enabled=preference.telegram_enabled
            )

            db_model = self._mapper.to_database_model(preference)
            self.session.add(db_model)
            await self.session.commit()

            logger.info(
                "User preference saved successfully",
                preference_id=str(preference.id)
            )
            return preference

        except IntegrityError as e:
            await self.session.rollback()
            logger.error(
                "Integrity error during user preference save",
                preference_id=str(preference.id),
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"User preference with this data already exists or constraint violated: {preference.id}") from e
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(
                "SQLAlchemy error during user preference save",
                preference_id=str(preference.id),
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Database error occurred while saving user preference with ID: {preference.id}") from e
        except Exception as e:
            await self.session.rollback()
            logger.error(
                "Unexpected error during user preference save",
                preference_id=str(preference.id),
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Unexpected error occurred while saving user preference with ID: {preference.id}") from e

    async def update(self, preference: UserPreferenceEntity) -> UserPreferenceEntity:
        """
        Update an existing user preference entity.

        Args:
            preference: User preference entity with updated data.

        Returns:
            Updated user preference entity.

        Raises:
            RepositoryError: If database operation fails.
        """
        try:
            logger.info(
                "Updating user preference",
                preference_id=str(preference.id),
                email=preference.email,
                email_enabled=preference.email_enabled,
                telegram_enabled=preference.telegram_enabled
            )

            dict_model = self._mapper.to_dict(preference)

            upd_stmt = (
                update(UserPreference)
                .where(UserPreference.id == preference.id)
                .values(dict_model)
                .returning(UserPreference)
            )

            result = await self.session.execute(upd_stmt)
            updated_model = result.scalar_one()

            logger.info(
                "User preference updated successfully",
                preference_id=str(preference.id)
            )
            return self._mapper.from_database_model(updated_model)

        except IntegrityError as e:
            await self.session.rollback()
            logger.error(
                "Integrity error during user preference update",
                preference_id=str(preference.id),
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"User preference update violates constraints: {preference.id}") from e
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(
                "SQLAlchemy error during user preference update",
                preference_id=str(preference.id),
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Database error occurred while updating user preference with ID: {preference.id}") from e
        except Exception as e:
            await self.session.rollback()
            logger.error(
                "Unexpected error during user preference update",
                preference_id=str(preference.id),
                error=str(e),
                exc_info=True
            )
            raise RepositoryError(f"Unexpected error occurred while updating user preference with ID: {preference.id}") from e