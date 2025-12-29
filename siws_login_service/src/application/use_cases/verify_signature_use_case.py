import structlog

from src.application.interfaces.repositories import NonceRepositoryProtocol
from src.domain.exceptions import (
    NonceNotFoundError,
    SignatureVerificationFailed,
    NonceAlreadyUsedError,
)
from src.infrastructures.crypto.ed25519_verifier import SignatureVerifier
from src.infrastructures.exceptions import (
    FailedToUpdateNonceError,
    InfrastructureError,
)

logger = structlog.getLogger(__name__)


class VerifySignatureUseCase:
    """Use case for verifying wallet signature during SIWS authentication.

    This use case handles the signature verification process for wallet-based
    authentication. It retrieves an active nonce for the wallet, verifies the
    cryptographic signature, and marks the nonce as used upon successful verification.

    The process involves:
    1. Finding an active nonce for the wallet address
    2. Verifying the signature against the nonce's message
    3. Marking the nonce as used to prevent replay attacks
    4. Returning the wallet address upon successful verification
    """

    def __init__(
        self,
        nonce_repository: NonceRepositoryProtocol,
        signature_verifier: SignatureVerifier,
    ) -> None:
        """Initialize the use case with required dependencies.

        Args:
            nonce_repository: Repository for nonce operations.
            signature_verifier: Service for verifying Ed25519 signatures.
        """
        self._repository = nonce_repository
        self._verifier = signature_verifier

    async def execute(
        self,
        signature: str,
        wallet_address: str,
    ) -> str:
        """Verify wallet signature and mark nonce as used.

        Verifies the cryptographic signature provided by the wallet against
        the active nonce's message. Upon successful verification, marks the
        nonce as used to prevent replay attacks.

        Args:
            signature: Base58-encoded Ed25519 signature to verify.
            wallet_address: Base58-encoded wallet address.

        Returns:
            The wallet address as a string upon successful verification.

        Raises:
            NonceNotFoundError: If no active nonce is found for the wallet.
            SignatureVerificationFailed: If signature verification fails.
            NonceAlreadyUsedError: If the nonce is already marked as used.
            FailedToUpdateNonceError: If updating nonce in database fails.
            InfrastructureError: If infrastructure operation fails.

        Example:
            >>> use_case = VerifySignatureUseCase(repo, verifier)
            >>> wallet = await use_case.execute(
            ...     signature="5KJvsngHeM...",
            ...     wallet_address="7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
            ... )
            >>> print(wallet)
            "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
        """
        try:
            logger.info(
                "Starting signature verification",
                wallet_address=wallet_address,
            )

            active_nonce = await self._repository.find_active_nonce_by_wallet(
                wallet_address
            )

            if active_nonce is None:
                logger.warning(
                    "Active nonce not found for wallet",
                    wallet_address=wallet_address,
                )
                raise NonceNotFoundError(
                    f"Active nonce not found for wallet address: {wallet_address}. "
                    "Maybe time is expired?"
                )

            logger.info(
                "Active nonce found, starting signature verification",
                wallet_address=wallet_address,
                nonce_uuid=str(active_nonce.uuid),
            )
            is_verified = await self._verifier.verify_signature(
                wallet_address=wallet_address,
                signature=signature,
            )

            if not is_verified:
                logger.error(
                    "Signature verification failed",
                    wallet_address=wallet_address,
                )
                raise SignatureVerificationFailed(
                    "Cannot confirm user's signature"
                )

            logger.info(
                "Signature verified successfully",
                wallet_address=wallet_address,
                nonce_uuid=str(active_nonce.uuid),
            )

            deactivated_nonce = active_nonce.mark_as_used()
            logger.info(
                "Nonce marked as used",
                wallet_address=wallet_address,
                nonce_uuid=str(deactivated_nonce.uuid),
            )

            await self._repository.update_nonce(
                nonce_uuid=str(deactivated_nonce.uuid),
                nonce_entity=deactivated_nonce,
            )

            logger.info(
                "Nonce updated in database successfully",
                wallet_address=wallet_address,
                nonce_uuid=str(deactivated_nonce.uuid),
            )

            return deactivated_nonce.wallet_address.value

        except NonceNotFoundError as e:
            logger.warning(
                "Active nonce not found",
                wallet_address=wallet_address,
                error=str(e),
            )
            raise

        except SignatureVerificationFailed as e:
            logger.error(
                "Signature verification failed",
                wallet_address=wallet_address,
                error=str(e),
            )
            raise

        except NonceAlreadyUsedError as e:
            logger.error(
                "Nonce already used",
                wallet_address=wallet_address,
                error=str(e),
            )
            raise

        except FailedToUpdateNonceError as e:
            logger.error(
                "Failed to update nonce in database",
                wallet_address=wallet_address,
                error=str(e),
                exc_info=True,
            )
            raise

        except InfrastructureError as e:
            logger.error(
                "Infrastructure error during signature verification",
                wallet_address=wallet_address,
                error=str(e),
                exc_info=True,
            )
            raise

        except Exception as e:
            logger.error(
                "Unexpected error during signature verification",
                wallet_address=wallet_address,
                error=str(e),
                exc_info=True,
            )
            raise InfrastructureError(
                f"Unexpected error during signature verification: {e}"
            ) from e