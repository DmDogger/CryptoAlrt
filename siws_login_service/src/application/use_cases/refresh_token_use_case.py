import structlog

from src.application.interfaces.token_issuer import RefreshTokenIssuerProtocol
from src.infrastructures.exceptions import TokenIssueError

logger = structlog.getLogger(__name__)


class RefreshTokenIssueUseCase:
    """Use case for issuing JWT refresh tokens.

    Handles the issuance of JWT refresh tokens for authenticated wallets.
    """

    def __init__(
        self,
        refresh_issuer: RefreshTokenIssuerProtocol,
    ) -> None:
        """Initialize the use case with required dependencies.

        Args:
            refresh_issuer: Token issuer for creating refresh tokens.
        """
        self._issuer = refresh_issuer

    def execute(
        self,
        wallet_address: str,
        device_id: str,
    ) -> str:
        """Issue a JWT refresh token for the given wallet address.

        Creates and returns a JWT refresh token for the specified wallet address.
        The token is signed using EdDSA algorithm and contains wallet address
        as the subject.

        Args:
            device_id: user's device
            wallet_address: The wallet address to issue token for.

        Returns:
            Encoded JWT refresh token string.

        Raises:
            TokenIssueError: If token issuance fails due to infrastructure error.
        """
        try:
            logger.info(
                "Issuing refresh token",
                wallet_address=wallet_address,
            )

            refresh_token = self._issuer.issue(
                sub=wallet_address,
                device_id=device_id,
            )

            logger.info(
                "Refresh token issued successfully",
                wallet_address=wallet_address,
            )

            return refresh_token

        except TokenIssueError as e:
            logger.error(
                "Token issue error during refresh token issuance",
                wallet_address=wallet_address,
                error=str(e),
                exc_info=True,
            )
            raise

        except Exception as e:
            logger.error(
                "Unexpected error during refresh token issuance",
                wallet_address=wallet_address,
                error=str(e),
                exc_info=True,
            )
            raise TokenIssueError(f"Unexpected error during refresh token issuance: {e}") from e
