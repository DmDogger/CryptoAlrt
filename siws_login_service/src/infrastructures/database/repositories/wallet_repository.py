from dataclasses import dataclass
from typing import final

import structlog
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructures.database.mappers.wallet_mapper import WalletDBMapper
from domain.entities.wallet_entity import WalletEntity
from infrastructures.database.models.wallet_model import Wallet
from infrastructures.exceptions import (
    FailedToSaveWalletError,
    InfrastructureError,
    FailedToUpdateWalletError,
    WalletNotFoundError,
)

from application.interfaces.repositories import WalletRepositoryProtocol

logger = structlog.getLogger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class SQLAlchemyWalletRepository(WalletRepositoryProtocol):
    """SQLAlchemy implementation of the Wallet Repository.

    This repository is responsible for database operations (CRUD) only.
    Mapping logic is delegated to WalletDBMapper following SRP.
    """
    _session: AsyncSession
    _mapper: WalletDBMapper

    async def get_wallet_by_address(
        self,
        wallet_address: str,
    ) -> WalletEntity | None:
        """Retrieve a wallet entity by its address.

        Args:
            wallet_address: The wallet address to search for.

        Returns:
            WalletEntity if found, None otherwise.

        Raises:
            InfrastructureError: If database operation fails.
        """
        try:
            logger.info(
                "Retrieving wallet by address",
                wallet_address=wallet_address,
            )
            stmt = (
                select(Wallet)
                .where(Wallet.wallet_address == wallet_address)
            )
            result = await self._session.scalars(stmt)
            wallet_model = result.first()

            if wallet_model is None:
                logger.warning(
                    "Wallet not found",
                    wallet_address=wallet_address,
                )
                return None

            logger.info(
                "Wallet retrieved successfully",
                wallet_address=wallet_address,
            )
            return self._mapper.from_database_model(wallet_model)
        except SQLAlchemyError as e:
            logger.error(
                "Database error during wallet retrieval",
                wallet_address=wallet_address,
                error=str(e),
                exc_info=True,
            )
            raise InfrastructureError(
                f"Failed to retrieve wallet with address: {wallet_address}"
            ) from e

    async def create_wallet(
        self,
        wallet_entity: WalletEntity,
    ) -> WalletEntity:
        """Create a new wallet entity in the database.

        Args:
            wallet_entity: The wallet entity to create.

        Returns:
            The created wallet entity.

        Raises:
            FailedToSaveWalletError: If database operation fails or
                integrity constraint is violated.
        """
        try:
            wallet_model = self._mapper.to_database_model(wallet_entity)
            logger.info(
                "Creating wallet",
                wallet_address=wallet_entity.wallet_address.value,
            )
            self._session.add(wallet_model)
            await self._session.commit()

            logger.info(
                "Wallet created successfully",
                wallet_address=wallet_entity.wallet_address.value,
            )
            return wallet_entity
        except IntegrityError as e:
            await self._session.rollback()
            logger.error(
                "Integrity error during wallet creation",
                wallet_address=wallet_entity.wallet_address.value,
                error=str(e),
                exc_info=True,
            )
            raise FailedToSaveWalletError(
                f"Wallet with address {wallet_entity.wallet_address.value} "
                f"already exists or constraint violated"
            ) from e
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(
                "Database error during wallet creation",
                wallet_address=wallet_entity.wallet_address.value,
                error=str(e),
                exc_info=True,
            )
            raise FailedToSaveWalletError(
                f"Failed to create wallet with address: "
                f"{wallet_entity.wallet_address.value}"
            ) from e

    async def update_values(
        self,
        wallet_address: str,
        wallet_entity: WalletEntity,
    ) -> WalletEntity:
        """Update wallet entity values in the database.

        Args:
            wallet_address: The wallet address to update.
            wallet_entity: The wallet entity with updated values.

        Returns:
            The updated wallet entity.

        Raises:
            WalletNotFoundError: If wallet with the given address is not found.
            FailedToUpdateWalletError: If database operation fails or
                integrity constraint is violated.
        """
        try:
            logger.info(
                "Updating wallet values",
                wallet_address=wallet_entity.wallet_address.value,
            )
            dict_entity = self._mapper.to_dict(wallet_entity)
            stmt = (
                update(Wallet)
                .where(Wallet.wallet_address == wallet_address)
                .values(dict_entity)
                .returning(Wallet)
            )
            result = await self._session.execute(stmt)
            updated_wallet = result.scalar_one_or_none()

            if updated_wallet is None:
                logger.warning(
                    "Wallet not found for update",
                    wallet_address=wallet_address,
                )
                raise WalletNotFoundError(
                    f"Cannot update wallet: wallet with address "
                    f"{wallet_address} not found"
                )

            await self._session.commit()

            logger.info(
                "Wallet updated successfully",
                wallet_address=wallet_entity.wallet_address.value,
            )
            return self._mapper.from_database_model(updated_wallet)
        except WalletNotFoundError:
            await self._session.rollback()
            raise
        except IntegrityError as e:
            await self._session.rollback()
            logger.error(
                "Integrity error during wallet update",
                wallet_address=wallet_entity.wallet_address.value,
                error=str(e),
                exc_info=True,
            )
            raise FailedToUpdateWalletError(
                f"Failed to update wallet with address "
                f"{wallet_entity.wallet_address.value}: constraint violated"
            ) from e
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(
                "Database error during wallet update",
                wallet_address=wallet_entity.wallet_address.value,
                error=str(e),
                exc_info=True,
            )
            raise FailedToUpdateWalletError(
                f"Failed to update wallet with address: "
                f"{wallet_entity.wallet_address.value}"
            ) from e
