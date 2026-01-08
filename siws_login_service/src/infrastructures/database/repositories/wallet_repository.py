from dataclasses import dataclass
from typing import final

import structlog
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructures.database.mappers.wallet_mapper import WalletDBMapper
from src.domain.entities.wallet_entity import WalletEntity
from src.infrastructures.database.models.wallet_model import Wallet
from src.infrastructures.exceptions import (
    FailedToSaveWalletError,
    InfrastructureError,
    FailedToUpdateWalletError,
    WalletNotFoundError,
)

from src.application.interfaces.repositories import WalletRepositoryProtocol
from src.domain.value_objects.wallet_session_vo import WalletSessionVO
from src.infrastructures.database.mappers.wallet_session_mapper import (
    WalletSessionDBMapper,
)
from src.infrastructures.exceptions import (
    SessionSaveFailed,
    RevokeSessionError,
    SessionError,
)
from src.infrastructures.database.models.wallet_model import WalletSession

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
    _wallet_session_mapper: WalletSessionDBMapper

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
            stmt = select(Wallet).where(Wallet.wallet_address == wallet_address)
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
                f"Failed to create wallet with address: " f"{wallet_entity.wallet_address.value}"
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
                    f"Cannot update wallet: wallet with address " f"{wallet_address} not found"
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
                f"Failed to update wallet with address: " f"{wallet_entity.wallet_address.value}"
            ) from e

    async def save_session(
        self,
        wallet_vo: WalletSessionVO,
    ) -> WalletSessionVO:
        """Save a wallet session to the database.

        Args:
            wallet_vo: The WalletSessionVO value object to save.

        Returns:
            The saved WalletSessionVO instance.

        Raises:
            SessionSaveFailed: If database operation fails or
                integrity constraint is violated.
        """
        try:
            session_model = self._wallet_session_mapper.to_database_model(wallet_vo)
            logger.info(
                "Saving wallet session to database",
                wallet_address=wallet_vo.wallet_address.value,
                device_id=wallet_vo.device_id,
            )
            self._session.add(session_model)
            await self._session.commit()

            logger.info(
                "Wallet session saved successfully",
                wallet_address=wallet_vo.wallet_address.value,
                device_id=wallet_vo.device_id,
            )
            await self._session.refresh(session_model)
            return self._wallet_session_mapper.from_database_model(session_model)
        except IntegrityError as e:
            await self._session.rollback()
            logger.error(
                "Integrity error during wallet session save",
                wallet_address=wallet_vo.wallet_address.value,
                device_id=wallet_vo.device_id,
                error=str(e),
                exc_info=True,
            )
            raise SessionSaveFailed(
                f"Failed to save wallet session: session with wallet address "
                f"{wallet_vo.wallet_address.value} and device_id {wallet_vo.device_id} "
                f"already exists or constraint violated"
            ) from e
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(
                "Database error during wallet session save",
                wallet_address=wallet_vo.wallet_address.value,
                device_id=wallet_vo.device_id,
                error=str(e),
                exc_info=True,
            )
            raise SessionSaveFailed(
                f"Failed to save wallet session for wallet address "
                f"{wallet_vo.wallet_address.value} and device_id {wallet_vo.device_id}: "
                f"database operation failed"
            ) from e
        except Exception as e:
            await self._session.rollback()
            logger.error(
                "Unexpected error during wallet session save",
                wallet_address=wallet_vo.wallet_address.value,
                device_id=wallet_vo.device_id,
                error=str(e),
                exc_info=True,
            )
            raise SessionSaveFailed(
                f"Unexpected error while saving wallet session for wallet address "
                f"{wallet_vo.wallet_address.value} and device_id {wallet_vo.device_id}: {e}"
            ) from e

    async def get_sessions_by_wallet(
        self,
        wallet_address: str,
    ) -> list[WalletSessionVO]:
        """Retrieve all wallet sessions for a given wallet address.

        Args:
            wallet_address: The wallet address to search for sessions.

        Returns:
            List of WalletSessionVO instances for the specified wallet address.
            Returns empty list if no sessions are found.

        Raises:
            SessionError: If database operation fails.
        """
        try:
            logger.info(
                "Retrieving wallet sessions by wallet address",
                wallet_address=wallet_address,
            )
            stmt = select(WalletSession).where(WalletSession.wallet_address == wallet_address)
            result = await self._session.scalars(stmt)
            sessions = result.all()

            if not sessions:
                logger.info(
                    "No wallet sessions found for wallet address",
                    wallet_address=wallet_address,
                )
                return []

            logger.info(
                "Wallet sessions retrieved successfully",
                wallet_address=wallet_address,
                sessions_count=len(sessions),
            )

            return [
                self._wallet_session_mapper.from_database_model(session_) for session_ in sessions
            ]
        except SQLAlchemyError as e:
            logger.error(
                "Database error during wallet sessions retrieval",
                wallet_address=wallet_address,
                error=str(e),
                exc_info=True,
            )
            raise SessionError(
                f"Failed to retrieve wallet sessions for wallet address "
                f"{wallet_address}: database operation failed"
            ) from e
        except Exception as e:
            logger.error(
                "Unexpected error during wallet sessions retrieval",
                wallet_address=wallet_address,
                error=str(e),
                exc_info=True,
            )
            raise SessionError(
                f"Unexpected error while retrieving wallet sessions for wallet address "
                f"{wallet_address}: {e}"
            ) from e

    async def get_session_by_device_id(
        self,
        wallet_address: str,
        device_id: str,
    ) -> WalletSessionVO | None:
        try:
            logger.info(
                "Trying to find active session by device ID",
                wallet_address=wallet_address,
                device_id=device_id,
            )
            stmt = select(WalletSession).where(
                WalletSession.wallet_address == wallet_address,
                WalletSession.device_id == device_id,
                WalletSession.is_revoked == False,
            )
            result = await self._session.execute(stmt)
            session = result.scalar_one_or_none()

            if session is None:
                logger.error(
                    "User session not found",
                    wallet_address=wallet_address,
                    device_id=device_id,
                )
                raise SessionError("Cannot find session")

            return self._wallet_session_mapper.from_database_model(session)
        except SQLAlchemyError as e:
            logger.error(
                "Database error during wallet session retrieval",
                wallet_address=wallet_address,
                device_id=device_id,
                error=str(e),
                exc_info=True,
            )
            raise SessionError(
                f"Failed to retrieve wallet sessions for wallet address "
                f"{wallet_address}: database operation failed"
            ) from e
        except Exception as e:
            logger.error(
                "Unexpected error during wallet sessions retrieval",
                wallet_address=wallet_address,
                device_id=device_id,
                error=str(e),
                exc_info=True,
            )
            raise SessionError(
                f"Unexpected error while retrieving wallet sessions for wallet address "
                f"{wallet_address}: {e}"
            ) from e


async def revoke_single_session(
    self,
    wallet_address: str,
    device_id: str,
) -> WalletSessionVO:
    """Revoke a single wallet session by wallet address and device ID.

    Updates the session's is_revoked flag to True in the database.

    Args:
        wallet_address: The wallet address of the session to revoke.
        device_id: The device ID of the session to revoke.

    Returns:
        The revoked WalletSessionVO instance.

    Raises:
        RevokeSessionError: If session is not found, database operation fails,
            or integrity constraint is violated.
    """
    try:
        logger.info(
            "Revoking wallet session",
            wallet_address=wallet_address,
            device_id=device_id,
        )
        stmt = (
            update(WalletSession)
            .where(
                WalletSession.wallet_address == wallet_address,
                WalletSession.device_id == device_id,
            )
            .values(is_revoked=True)
            .returning(WalletSession)
        )
        result = await self._session.execute(stmt)
        revoked_session = result.scalar_one_or_none()

        if revoked_session is None:
            logger.warning(
                "Wallet session not found for revocation",
                wallet_address=wallet_address,
                device_id=device_id,
            )
            raise RevokeSessionError(
                f"Failed to revoke wallet session: session with wallet address "
                f"{wallet_address} and device_id {device_id} not found"
            )

        await self._session.commit()

        logger.info(
            "Wallet session revoked successfully",
            wallet_address=wallet_address,
            device_id=device_id,
        )
        return self._wallet_session_mapper.from_database_model(revoked_session)

    except RevokeSessionError:
        await self._session.rollback()
        raise
    except IntegrityError as e:
        await self._session.rollback()
        logger.error(
            "Integrity error during wallet session revocation",
            wallet_address=wallet_address,
            device_id=device_id,
            error=str(e),
            exc_info=True,
        )
        raise RevokeSessionError(
            f"Failed to revoke wallet session for wallet address "
            f"{wallet_address} and device_id {device_id}: constraint violated"
        ) from e
    except SQLAlchemyError as e:
        await self._session.rollback()
        logger.error(
            "Database error during wallet session revocation",
            wallet_address=wallet_address,
            device_id=device_id,
            error=str(e),
            exc_info=True,
        )
        raise RevokeSessionError(
            f"Failed to revoke wallet session for wallet address "
            f"{wallet_address} and device_id {device_id}: database operation failed"
        ) from e
    except Exception as e:
        await self._session.rollback()
        logger.error(
            "Unexpected error during wallet session revocation",
            wallet_address=wallet_address,
            device_id=device_id,
            error=str(e),
            exc_info=True,
        )
        raise RevokeSessionError(
            f"Unexpected error while revoking wallet session for wallet address "
            f"{wallet_address} and device_id {device_id}: {e}"
        ) from e


async def terminate_all_sessions(
    self,
    wallet_address: str,
) -> list[WalletSessionVO]:
    """Terminate all wallet sessions for a given wallet address.

    Updates all sessions' is_revoked flag to True in the database for the specified wallet.

    Args:
        wallet_address: The wallet address for which to terminate all sessions.

    Returns:
        List of revoked WalletSessionVO instances.

    Raises:
        RevokeSessionError: If database operation fails or integrity constraint is violated.
    """
    try:
        logger.info(
            "Terminating all wallet sessions",
            wallet_address=wallet_address,
        )
        stmt = (
            update(WalletSession)
            .where(WalletSession.wallet_address == wallet_address)
            .values(is_revoked=True)
            .returning(WalletSession)
        )
        result = await self._session.execute(stmt)
        revoked_sessions = result.scalars().all()
        logger.debug("revoked sessions executed", debug_len=len(revoked_sessions))

        await self._session.commit()
        logger.debug("revoked", debug_revs=revoked_sessions)

        if not revoked_sessions:
            logger.warning(
                "No wallet sessions found to terminate",
                wallet_address=wallet_address,
            )
            raise RevokeSessionError(
                f"Failed to terminate wallet sessions: no active sessions found "
                f"for wallet address {wallet_address}"
            )

        logger.info(
            "All wallet sessions terminated successfully",
            wallet_address=wallet_address,
            sessions_count=len(revoked_sessions),
        )

        return [
            self._wallet_session_mapper.from_database_model(session) for session in revoked_sessions
        ]

    except IntegrityError as e:
        await self._session.rollback()
        logger.error(
            "Integrity error during wallet sessions termination",
            wallet_address=wallet_address,
            error=str(e),
            exc_info=True,
        )
        raise RevokeSessionError(
            f"Failed to terminate all wallet sessions for wallet address "
            f"{wallet_address}: constraint violated"
        ) from e
    except SQLAlchemyError as e:
        await self._session.rollback()
        logger.error(
            "Database error during wallet sessions termination",
            wallet_address=wallet_address,
            error=str(e),
            exc_info=True,
        )
        raise RevokeSessionError(
            f"Failed to terminate all wallet sessions for wallet address "
            f"{wallet_address}: database operation failed"
        ) from e
    except Exception as e:
        await self._session.rollback()
        logger.error(
            "Unexpected error during wallet sessions termination",
            wallet_address=wallet_address,
            error=str(e),
            exc_info=True,
        )
        raise RevokeSessionError(
            f"Unexpected error while terminating all wallet sessions for wallet address "
            f"{wallet_address}: {e}"
        ) from e
