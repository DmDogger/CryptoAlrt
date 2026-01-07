import structlog
from sqlalchemy.exc import IntegrityError

from src.infrastructures.database.repositories.wallet_repository import (
    SQLAlchemyWalletRepository,
)
from src.infrastructures.exceptions import (
    WalletNotFoundError,
    SessionError,
    RevokeSessionError,
)

logger = structlog.getLogger(__name__)


class RevokeSessionUseCase:
    """Use case for revoking a single wallet session.

    Handles the revocation of a wallet session by wallet address and device ID.
    Validates that the wallet exists and has active sessions before revoking.
    """

    def __init__(self, wallet_repository: SQLAlchemyWalletRepository) -> None:
        """Initialize the use case with required dependencies.

        Args:
            wallet_repository: Repository for wallet and session operations.
        """
        self._repository = wallet_repository

    async def execute(
        self,
        wallet_address: str,
        device_id: str,
    ) -> "WalletSessionVO":
        """Revoke a single wallet session for the given wallet address and device ID.

        Validates that the wallet exists, has active sessions, and then revokes
        the session associated with the specified device ID.

        Args:
            wallet_address: The wallet address to revoke session for.
            device_id: The device ID of the session to revoke.

        Raises:
            WalletNotFoundError: If the wallet with the given address is not found.
            SessionError: If no active sessions are found for the wallet, or if
                the specific session cannot be found, or if an error occurs
                during session revocation.
        """
        try:
            wallet = await self._repository.get_wallet_by_address(
                wallet_address=wallet_address,
            )

            if not wallet:
                logger.error(
                    "Wallet not found to terminate session",
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

            terminated = await self._repository.revoke_single_session(
                wallet_address=wallet_address,
                device_id=device_id,
            )

            if not terminated:
                logger.error(
                    "No session found to terminate",
                    device_id=device_id,
                    wallet_address=wallet_address,
                )
                raise SessionError(
                    f"Cannot find session to terminate for wallet: {wallet_address}, device: {device_id}"
                )

            return terminated

        except RevokeSessionError as e:
            logger.error(
                "Error occurred during session termination",
                error=str(e),
                device_id=device_id,
                wallet_address=wallet_address,
                exc_info=True,
            )
            raise SessionError(
                f"Error occurred during session termination "
                f"for address: {wallet_address}, "
                f"device id: {device_id}"
            ) from e

        except Exception as e:
            logger.error(
                "Unexpected error occurred during session termination",
                error=str(e),
                device_id=device_id,
                wallet_address=wallet_address,
                exc_info=True,
            )
            raise SessionError(
                f"Unexpected error occurred during session termination "
                f"for address: {wallet_address}, "
                f"device id: {device_id}"
            ) from e
