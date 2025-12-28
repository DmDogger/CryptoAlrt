from dataclasses import dataclass
from typing import final

import structlog
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from domain.exceptions import NonceNotFoundError, SignatureVerificationFailed
from domain.value_objects.message_vo import MessageVO
from domain.value_objects.signature_vo import SignatureVO
from domain.value_objects.wallet_vo import WalletAddressVO
from infrastructures.database.repositories.nonce_repository import SQLAlchemyNonceRepository

logger = structlog.getLogger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class SignatureVerifier:
    """Ed25519 signature verifier for Solana wallet authentication.

    This verifier validates cryptographic signatures using Ed25519 algorithm
    for SIWE (Sign-In With Ethereum/Solana) authentication flow.
    """

    _nonce_repository: SQLAlchemyNonceRepository

    async def verify_signature(
        self,
        wallet_address: str,
        signature: str,
    ) -> bool:
        """Verify Ed25519 signature for wallet authentication.

        Validates that the provided signature was created by the wallet owner
        signing the SIWE message associated with an active nonce.

        Args:
            wallet_address: Base58-encoded wallet address.
            signature: Base58-encoded signature to verify.

        Raises:
            NonceNotFoundError: If no active nonce is found for the wallet.
            SignatureVerificationFailed: If signature verification fails.
        """
        try:
            logger.info(
                "Starting signature verification",
                wallet_address=wallet_address,
            )
            existing_nonce = await self._nonce_repository.find_active_nonce_by_wallet(
                wallet_address
            )
            if not existing_nonce:
                logger.error(
                    "Active nonce not found for wallet",
                    wallet_address=wallet_address,
                )
                raise NonceNotFoundError(
                    f"Active nonce not found for wallet address: {wallet_address}"
                )

            signature_vo = SignatureVO.from_string(signature)
            bytes_signature = signature_vo.to_bytes()
            logger.info(
                "Signature converted to bytes",
                wallet_address=wallet_address,
            )

            message = MessageVO.from_record(existing_nonce)
            string_message = message.to_string()
            bytes_message = string_message.encode("utf-8")
            logger.info(
                "Message converted to bytes",
                wallet_address=wallet_address,
            )

            wallet_vo = WalletAddressVO.from_string(wallet_address)
            bytes_wallet = wallet_vo.to_bytes()
            logger.info(
                "Wallet address converted to bytes",
                wallet_address=wallet_address,
            )

            logger.info(
                "Verifying signature",
                wallet_address=wallet_address,
            )
            verify_key = VerifyKey(bytes_wallet)
            verify_key.verify(bytes_message, bytes_signature)
            logger.info(
                "Signature verified successfully",
                wallet_address=wallet_address,
            )
            return True

        except NonceNotFoundError:
            raise
        except BadSignatureError as e:
            logger.error(
                "Signature verification failed",
                wallet_address=wallet_address,
                error=str(e),
                exc_info=True,
            )
            raise SignatureVerificationFailed(
                f"Signature verification failed for wallet address: {wallet_address}"
            ) from e





