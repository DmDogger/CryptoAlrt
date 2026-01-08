"""Use case for issuing JWT access tokens.

Creates short-lived access tokens for authenticated wallet sessions.
"""
import structlog

from src.application.interfaces.token_issuer import AccessTokenIssuerProtocol
from src.infrastructures.exceptions import TokenIssueError

logger = structlog.getLogger(__name__)


class AccessTokenIssueUseCase:
    """Use case for issuing JWT access tokens.

    Handles the issuance of JWT access tokens for authenticated wallets.
    """

    def __init__(
        self,
        access_issuer: AccessTokenIssuerProtocol,
    ) -> None:
        """Initialize the use case with required dependencies.

        Args:
            access_issuer: Token issuer for creating access tokens.
        """
        self._issuer = access_issuer

    def execute(
        self,
        wallet_address: str,
    ) -> str:
        """Issue a JWT access token for the given wallet address.

        Creates and returns a JWT access token for the specified wallet address.
        The token is signed using EdDSA algorithm and contains wallet address
        as the subject.

        Args:
            wallet_address: The wallet address to issue token for.

        Returns:
            Encoded JWT access token string.

        Raises:
            TokenIssueError: If token issuance fails due to infrastructure error.
        """
        try:
            logger.info(
                "Issuing access token",
                wallet_address=wallet_address,
            )

            access_token = self._issuer.issue(
                sub=wallet_address,
            )

            logger.info(
                "Access token issued successfully",
                wallet_address=wallet_address,
            )

            return access_token

        except TokenIssueError as e:
            logger.error(
                "Token issue error during access token issuance",
                wallet_address=wallet_address,
                error=str(e),
                exc_info=True,
            )
            raise

        except Exception as e:
            logger.error(
                "Unexpected error during access token issuance",
                wallet_address=wallet_address,
                error=str(e),
                exc_info=True,
            )
            raise TokenIssueError(f"Unexpected error during access token issuance: {e}") from e
