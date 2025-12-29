"""Crypto providers for Dishka dependency injection."""

from dishka import Provider, Scope, provide

from src.infrastructures.crypto.ed25519_verifier import SignatureVerifier
from src.infrastructures.database.repositories.nonce_repository import (
    SQLAlchemyNonceRepository,
)


class CryptoProvider(Provider):
    """Provider for crypto-related dependencies."""

    @provide(scope=Scope.REQUEST)
    def provide_signature_verifier(
        self,
        nonce_repository: SQLAlchemyNonceRepository,
    ) -> SignatureVerifier:
        """Provide SignatureVerifier instance."""
        return SignatureVerifier(_nonce_repository=nonce_repository)
