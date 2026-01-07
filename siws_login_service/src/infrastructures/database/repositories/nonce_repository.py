from dataclasses import dataclass
from datetime import datetime, UTC
from typing import final

import structlog
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructures.database.mappers.nonce_mapper import NonceDBMapper
from src.domain.entities.nonce_entity import NonceEntity
from src.infrastructures.database.models.nonce_model import Nonce
from src.infrastructures.exceptions import (
    FailedToSaveNonceError,
    InfrastructureError,
    FailedToUpdateNonceError,
    NonceNotFoundError,
)

logger = structlog.getLogger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class SQLAlchemyNonceRepository:
    """SQLAlchemy implementation of the Nonce Repository.

    This repository is responsible for database operations (CRUD) only.
    Mapping logic is delegated to NonceDBMapper following SRP.
    """

    _session: AsyncSession
    _mapper: NonceDBMapper

    async def find_active_nonce_by_wallet(
        self,
        wallet_address: str,
    ) -> NonceEntity | None:
        """Retrieve an active nonce entity by wallet address.

        An active nonce is one that:
        - Has not been used (used_at is None)
        - Has not expired (expiration_time > current time)

        Args:
            wallet_address: The wallet address to search for.

        Returns:
            NonceEntity if an active nonce is found, None otherwise.

        Raises:
            InfrastructureError: If database operation fails.
        """
        try:
            logger.info(
                "Retrieving active nonce by wallet address",
                wallet_address=wallet_address,
            )
            current_time = datetime.now(UTC)
            stmt = select(Nonce).where(
                Nonce.wallet_address == wallet_address,
                Nonce.used_at.is_(None),
                Nonce.expiration_time > current_time,
            )
            result = await self._session.scalars(stmt)
            nonce_model = result.first()

            if nonce_model is None:
                logger.warning(
                    "Active nonce not found",
                    wallet_address=wallet_address,
                )
                return None

            logger.info(
                "Active nonce retrieved successfully",
                wallet_address=wallet_address,
            )
            return self._mapper.from_database_model(nonce_model)
        except SQLAlchemyError as e:
            logger.error(
                "Database error during active nonce retrieval",
                wallet_address=wallet_address,
                error=str(e),
                exc_info=True,
            )
            raise InfrastructureError(
                f"Failed to retrieve active nonce for wallet address: {wallet_address}"
            ) from e

    async def find_nonce_by_wallet(
        self,
        wallet_address: str,
    ) -> NonceEntity | None:
        """Retrieve a nonce entity by wallet address.

        Args:
            wallet_address: The wallet address to search for.

        Returns:
            NonceEntity if found, None otherwise.

        Raises:
            InfrastructureError: If database operation fails.
        """
        try:
            logger.info(
                "Retrieving nonce by wallet address",
                wallet_address=wallet_address,
            )
            stmt = select(Nonce).where(Nonce.wallet_address == wallet_address)
            result = await self._session.scalars(stmt)
            nonce_model = result.first()

            if nonce_model is None:
                logger.warning(
                    "Nonce not found",
                    wallet_address=wallet_address,
                )
                return None

            logger.info(
                "Nonce retrieved successfully",
                wallet_address=wallet_address,
            )
            return self._mapper.from_database_model(nonce_model)
        except SQLAlchemyError as e:
            logger.error(
                "Database error during nonce retrieval",
                wallet_address=wallet_address,
                error=str(e),
                exc_info=True,
            )
            raise InfrastructureError(
                f"Failed to retrieve nonce for wallet address: {wallet_address}"
            ) from e

    async def create_nonce(
        self,
        nonce_entity: NonceEntity,
    ) -> NonceEntity:
        """Create a new nonce entity in the database.

        Args:
            nonce_entity: The nonce entity to create.

        Returns:
            The created nonce entity.

        Raises:
            FailedToSaveNonceError: If database operation fails or
                integrity constraint is violated.
        """
        try:
            nonce_model = self._mapper.to_database_model(nonce_entity)
            logger.info(
                "Creating nonce",
                nonce_uuid=str(nonce_entity.uuid),
                wallet_address=nonce_entity.wallet_address.value,
            )
            self._session.add(nonce_model)
            await self._session.commit()

            logger.info(
                "Nonce created successfully",
                nonce_uuid=str(nonce_entity.uuid),
                wallet_address=nonce_entity.wallet_address.value,
            )

            reloaded_nonce = await self._session.get(Nonce, nonce_entity.uuid)
            logger.info(
                "Found created nonce, returning back >>>",
                nonce_uuid=str(nonce_entity.uuid),
                wallet_address=nonce_entity.wallet_address.value,
            )

            return self._mapper.from_database_model(reloaded_nonce)

        except IntegrityError as e:
            await self._session.rollback()
            logger.error(
                "Integrity error during nonce creation",
                nonce_uuid=str(nonce_entity.uuid),
                wallet_address=nonce_entity.wallet_address.value,
                error=str(e),
                exc_info=True,
            )
            raise FailedToSaveNonceError(
                f"Nonce with UUID {nonce_entity.uuid} already exists "
                f"or constraint violated"
            ) from e

        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(
                "Database error during nonce creation",
                nonce_uuid=str(nonce_entity.uuid),
                wallet_address=nonce_entity.wallet_address.value,
                error=str(e),
                exc_info=True,
            )
            raise FailedToSaveNonceError(
                f"Failed to create nonce with UUID: {nonce_entity.uuid}"
            ) from e

    async def update_nonce(
        self,
        nonce_uuid: str,
        nonce_entity: NonceEntity,
    ) -> NonceEntity:
        """Update nonce entity values in the database.

        Args:
            nonce_uuid: The nonce UUID to update.
            nonce_entity: The nonce entity with updated values.

        Returns:
            The updated nonce entity.

        Raises:
            NonceNotFoundError: If nonce with the given UUID is not found.
            FailedToUpdateNonceError: If database operation fails or
                integrity constraint is violated.
        """
        try:
            logger.info(
                "Updating nonce values",
                nonce_uuid=nonce_uuid,
                wallet_address=nonce_entity.wallet_address.value,
            )
            dict_entity = self._mapper.to_dict(nonce_entity)
            stmt = (
                update(Nonce)
                .where(Nonce.uuid == nonce_uuid)
                .values(dict_entity)
                .returning(Nonce)
            )
            result = await self._session.execute(stmt)
            updated_nonce = result.scalar_one_or_none()

            if updated_nonce is None:
                logger.warning(
                    "Nonce not found for update",
                    nonce_uuid=nonce_uuid,
                )
                raise NonceNotFoundError(
                    f"Cannot update nonce: nonce with UUID {nonce_uuid} not found"
                )

            await self._session.commit()

            logger.info(
                "Nonce updated successfully",
                nonce_uuid=nonce_uuid,
                wallet_address=nonce_entity.wallet_address.value,
            )
            return self._mapper.from_database_model(updated_nonce)
        except NonceNotFoundError:
            await self._session.rollback()
            raise
        except IntegrityError as e:
            await self._session.rollback()
            logger.error(
                "Integrity error during nonce update",
                nonce_uuid=nonce_uuid,
                wallet_address=nonce_entity.wallet_address.value,
                error=str(e),
                exc_info=True,
            )
            raise FailedToUpdateNonceError(
                f"Failed to update nonce with UUID {nonce_uuid}: constraint violated"
            ) from e
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(
                "Database error during nonce update",
                nonce_uuid=nonce_uuid,
                wallet_address=nonce_entity.wallet_address.value,
                error=str(e),
                exc_info=True,
            )
            raise FailedToUpdateNonceError(
                f"Failed to update nonce with UUID: {nonce_uuid}"
            ) from e
