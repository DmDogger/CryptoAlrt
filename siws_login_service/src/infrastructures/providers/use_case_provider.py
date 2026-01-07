"""Use case providers for Dishka dependency injection."""

from dishka import Provider, Scope, provide

from src.application.interfaces.event_publisher import EventPublisherProtocol
from src.application.interfaces.repositories import (
    NonceRepositoryProtocol,
    WalletRepositoryProtocol,
)
from src.application.interfaces.token_issuer import (
    AccessTokenIssuerProtocol,
    RefreshTokenIssuerProtocol,
)
from src.application.use_cases.access_token_use_case import AccessTokenIssueUseCase
from src.application.use_cases.refresh_token_use_case import RefreshTokenIssueUseCase
from src.application.use_cases.send_message_to_broker import SendUserLoggedUseCase
from src.application.use_cases.send_request_use_case import SendRequestUseCase
from src.application.use_cases.terminate_sessions_use_case import (
    TerminateSessionsUseCase,
)
from src.application.use_cases.tokens_issuer_use_case import TokensIssuerUseCase
from src.application.use_cases.verify_signature_use_case import VerifySignatureUseCase
from src.infrastructures.crypto.ed25519_verifier import SignatureVerifier
from src.infrastructures.database.repositories.wallet_repository import (
    SQLAlchemyWalletRepository,
)


class UseCaseProvider(Provider):
    """Provider for use case dependencies."""

    @provide(scope=Scope.REQUEST)
    def provide_send_request_use_case(
        self,
        nonce_repository: NonceRepositoryProtocol,
        wallet_repository: WalletRepositoryProtocol,
    ) -> SendRequestUseCase:
        """Provide SendRequestUseCase instance."""
        return SendRequestUseCase(
            nonce_repository=nonce_repository,
            wallet_repository=wallet_repository,
        )

    @provide(scope=Scope.REQUEST)
    def provide_access_token_issue_use_case(
        self,
        access_issuer: AccessTokenIssuerProtocol,
    ) -> AccessTokenIssueUseCase:
        """Provide AccessTokenIssueUseCase instance."""
        return AccessTokenIssueUseCase(access_issuer=access_issuer)

    @provide(scope=Scope.REQUEST)
    def provide_refresh_token_issue_use_case(
        self,
        refresh_issuer: RefreshTokenIssuerProtocol,
    ) -> RefreshTokenIssueUseCase:
        """Provide RefreshTokenIssueUseCase instance."""
        return RefreshTokenIssueUseCase(refresh_issuer=refresh_issuer)

    @provide(scope=Scope.REQUEST)
    def provide_tokens_issuer_use_case(
        self,
        access_issuer_uc: AccessTokenIssueUseCase,
        refresh_issuer_uc: RefreshTokenIssueUseCase,
        wallet_repository: SQLAlchemyWalletRepository,
    ) -> TokensIssuerUseCase:
        """Provide TokensIssuerUseCase instance."""
        return TokensIssuerUseCase(
            access_issuer_uc=access_issuer_uc,
            refresh_issuer_uc=refresh_issuer_uc,
            wallet_repository=wallet_repository,
        )

    @provide(scope=Scope.REQUEST)
    def provide_verify_signature_use_case(
        self,
        nonce_repository: NonceRepositoryProtocol,
        signature_verifier: SignatureVerifier,
        issuer: TokensIssuerUseCase,
    ) -> VerifySignatureUseCase:
        """Provide VerifySignatureUseCase instance."""
        return VerifySignatureUseCase(
            nonce_repository=nonce_repository,
            signature_verifier=signature_verifier,
            issuer=issuer,
        )

    @provide(scope=Scope.REQUEST)
    def provide_send_user_logged_use_case(
        self,
        event_publisher: EventPublisherProtocol,
    ) -> SendUserLoggedUseCase:
        """Provide SendUserLoggedUseCase instance."""
        return SendUserLoggedUseCase(broker=event_publisher)

    @provide(scope=Scope.REQUEST)
    def provide_terminate_sessions_use_case(
        self,
        wallet_repository: SQLAlchemyWalletRepository,
    ) -> TerminateSessionsUseCase:
        """Provide TerminateSessionsUseCase instance."""
        return TerminateSessionsUseCase(repository=wallet_repository)
