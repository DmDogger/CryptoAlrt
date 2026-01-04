import structlog
from typing import TYPE_CHECKING

from src.infrastructures.database.repositories.wallet_repository import SQLAlchemyWalletRepository
from src.infrastructures.exceptions import (
    WalletNotFoundError,
    SessionError,
    RevokeSessionError,
)

if TYPE_CHECKING:
    from src.domain.value_objects.wallet_session_vo import WalletSessionVO

logger = structlog.getLogger(__name__)


class TerminateSessionsUseCase:
    """Use case for terminating all wallet sessions.

    Handles the termination of all active sessions for a given wallet address.
    Validates that the wallet exists and has active sessions before terminating.
    """

    def __init__(
        self,
        repository: SQLAlchemyWalletRepository,
    ) -> None:
        """Initialize the use case with required dependencies.

        Args:
            repository: Repository for wallet and session operations.
        """
        self._repository = repository

    async def execute(
        self,
        wallet_address: str,
    ) -> list["WalletSessionVO"]:
        """Terminate all wallet sessions for the given wallet address.

        Validates that the wallet exists, has active sessions, and then terminates
        all sessions associated with the specified wallet address.

        Args:
            wallet_address: The wallet address to terminate sessions for.

        Returns:
            List of terminated WalletSessionVO instances.

        Raises:
            WalletNotFoundError: If the wallet with the given address is not found.
            SessionError: If no active sessions are found for the wallet, or if
                an error occurs during session termination.
        """
        try:
            logger.info(
                "Terminating all wallet sessions",
                wallet_address=wallet_address,
            )

            wallet = await self._repository.get_wallet_by_address(
                wallet_address=wallet_address,
            )

            if not wallet:
                logger.error(
                    "Wallet not found to terminate sessions",
                    wallet_address=wallet_address,
                )
                raise WalletNotFoundError(
                    f"Wallet not found with address: {wallet_address}"
                )

            sessions = await self._repository.get_sessions_by_wallet(
                wallet_address=wallet.wallet_address.value,
            )

            if not sessions:
                logger.error(
                    "No active sessions found",
                    wallet_address=wallet_address,
                )
                raise SessionError(
                    f"Cannot find at least one active session for wallet: {wallet_address}"
                )

            terminated_sessions = await self._repository.terminate_all_sessions(
                wallet_address=wallet_address
            )

            if not terminated_sessions:
                logger.error(
                    "No sessions terminated",
                    wallet_address=wallet_address,
                )
                raise SessionError(
                    f"Failed to terminate sessions for wallet: {wallet_address}"
                )

            logger.info(
                "All wallet sessions terminated successfully",
                wallet_address=wallet_address,
                sessions_count=len(terminated_sessions),
            )

            return terminated_sessions

        except RevokeSessionError as e:
            logger.error(
                "Error occurred during sessions termination",
                error=str(e),
                wallet_address=wallet_address,
                exc_info=True,
            )
            raise SessionError(
                f"Error occurred during sessions termination "
                f"for address: {wallet_address}"
            ) from e

        except Exception as e:
            logger.error(
                "Unexpected error occurred during sessions termination",
                error=str(e),
                wallet_address=wallet_address,
                exc_info=True,
            )
            raise SessionError(
                f"Unexpected error occurred during sessions termination "
                f"for address: {wallet_address}"
            ) from e