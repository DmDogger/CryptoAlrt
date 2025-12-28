from typing import Protocol


class SignatureVerifierProtocol(Protocol):
    """Protocol for a signature verifier.

    Defines methods for verifying cryptographic signatures for wallet authentication.
    """

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

        Returns:
            True if signature is valid.

        Raises:
            NonceNotFoundError: If no active nonce is found for the wallet.
            SignatureVerificationFailed: If signature verification fails.
        """
        ...
