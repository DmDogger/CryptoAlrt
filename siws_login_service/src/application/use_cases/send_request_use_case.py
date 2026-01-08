import structlog

from src.application.interfaces.repositories import (
    NonceRepositoryProtocol,
    WalletRepositoryProtocol,
)
from src.domain.entities.nonce_entity import NonceEntity
from src.domain.entities.wallet_entity import WalletEntity
from src.domain.value_objects.wallet_vo import WalletAddressVO
from src.domain.value_objects.nonce_vo import NonceVO
from src.domain.value_objects.message_vo import MessageVO
from src.infrastructures.exceptions import (
    InfrastructureError,
    FailedToSaveNonceError,
)

logger = structlog.getLogger(__name__)


class SendRequestUseCase:
    """Use case for generating SIWE message for wallet authentication.

    Handles the creation or retrieval of nonce and generates a SIWE message
    that the user needs to sign for authentication.
    """

    def __init__(
        self,
        nonce_repository: NonceRepositoryProtocol,
        wallet_repository: WalletRepositoryProtocol,
    ) -> None:
        """Initialize the use case with required dependencies.

        Args:
            nonce_repository: Repository for nonce operations.
            wallet_repository: Repository for wallet operations.
        """
        self._nonce_repository = nonce_repository
        self._wallet_repository = wallet_repository

    async def execute(
        self,
        wallet_address: str,
    ) -> str:
        """Generate SIWE message for wallet authentication.

        Checks for an existing active nonce for the wallet. If found,
        returns a message based on that nonce. Otherwise, creates a new
        nonce and returns a message based on it.

        Args:
            wallet_address: The wallet address to generate message for.

        Returns:
            SIWE message string ready for user signing.

        Raises:
            InfrastructureError: If database operation fails during nonce retrieval.
            FailedToSaveNonceError: If nonce creation fails.
            DomainError: If domain validation fails during nonce entity creation.
        """
        try:
            logger.info(
                "Generating SIWE message for wallet",
                wallet_address=wallet_address,
            )
            existing_nonce = await self._nonce_repository.find_active_nonce_by_wallet(
                wallet_address
            )

            if existing_nonce is not None:
                logger.info(
                    "Active nonce found, reusing existing nonce",
                    wallet_address=wallet_address,
                )
                message_for_existing_nonce = MessageVO.from_record(existing_nonce)
                return message_for_existing_nonce.to_string()

            logger.info(
                "No active nonce found, creating new nonce",
                wallet_address=wallet_address,
            )

            # TODO: Create wallet if not exist
            wallet_address_vo = WalletAddressVO(value=wallet_address)
            existing_wallet = await self._wallet_repository.get_wallet_by_address(wallet_address)
            if existing_wallet is None:
                logger.info(
                    "Wallet not found, creating new wallet",
                    wallet_address=wallet_address,
                )
                wallet_entity = WalletEntity.create(wallet_address=wallet_address_vo)
                await self._wallet_repository.create_wallet(wallet_entity)

            nonce_to_save = NonceEntity.create(
                wallet_address=wallet_address_vo,
                nonce=NonceVO.generate(),
                statement="Powered by DmDogg",
            )
            saved_nonce = await self._nonce_repository.create_nonce(nonce_to_save)

            message = MessageVO.from_record(saved_nonce)
            logger.info(
                "Nonce created successfully, SIWS message generated",
                wallet_address=wallet_address,
            )
            return message.to_string()

        except InfrastructureError as e:
            logger.error(
                "Infrastructure error during nonce retrieval",
                wallet_address=wallet_address,
                error=str(e),
                exc_info=True,
            )
            raise

        except FailedToSaveNonceError as e:
            logger.error(
                "Failed to save nonce to database",
                wallet_address=wallet_address,
                error=str(e),
                exc_info=True,
            )
            raise

        except Exception as e:
            logger.error(
                "Unexpected error during SIWE message generation",
                wallet_address=wallet_address,
                error=str(e),
                exc_info=True,
            )
            raise InfrastructureError(
                f"Unexpected error during SIWS message generation: {e}"
            ) from e
