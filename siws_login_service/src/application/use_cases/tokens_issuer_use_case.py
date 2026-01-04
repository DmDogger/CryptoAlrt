import structlog

from src.application.use_cases.access_token_use_case import AccessTokenIssueUseCase
from src.application.use_cases.refresh_token_use_case import RefreshTokenIssueUseCase
from src.domain.exceptions import TokenValidationError
from src.domain.value_objects.token_vo import TokenPairVO
from src.infrastructures.exceptions import InfrastructureError

logger = structlog.getLogger(__name__)


class TokensIssuerUseCase:
    """Use case for issuing both access and refresh tokens.

    Handles the issuance of JWT access and refresh tokens.
    """

    def __init__(
        self,
        access_issuer_uc: AccessTokenIssueUseCase,
        refresh_issuer_uc: RefreshTokenIssueUseCase,
    ) -> None:
        """Initialize the use case with required dependencies.

        Args:
            access_issuer_uc: Use case for issuing access tokens.
            refresh_issuer_uc: Use case for issuing refresh tokens.
        """
        self._access_issuer = access_issuer_uc
        self._refresh_issuer = refresh_issuer_uc

    async def execute(
        self,
        wallet_address: str,
    ) -> TokenPairVO:
        """Issue access and refresh tokens for the given wallet address.

        Creates both access and refresh JWT tokens.

        Args:
            wallet_address: The wallet address to issue tokens for.

        Returns:
            TokenPairVO containing both access and refresh tokens.

        Raises:
            TokenValidationError: If token creation fails validation.
            InfrastructureError: If unexpected error occurs during token issuance.
        """
        try:
            logger.info(
                "Issuing access and refresh tokens",
                wallet_address=wallet_address,
            )

            access_token = self._access_issuer.execute(wallet_address)
            refresh_token = self._refresh_issuer.execute(wallet_address)

            logger.info(
                "Tokens issued successfully",
                wallet_address=wallet_address,
            )
            #TODO: добавить wallet_repo, будем добавлять сессию в репозиторий
            #TODO: scrypt тоже (хешируем токен)
            #TODO: добавляем сессию при выпуске токенов

            tokens = TokenPairVO.from_string(
                access_token=access_token,
                refresh_token=refresh_token,
            )

            return tokens

        except TokenValidationError as e:
            logger.error(
                "Token validation error during token issuance",
                wallet_address=wallet_address,
                error=str(e),
                exc_info=True,
            )
            raise

        except Exception as e:
            logger.error(
                "Unexpected error during token issuance",
                wallet_address=wallet_address,
                error=str(e),
                exc_info=True,
            )
            raise InfrastructureError(
                f"Unexpected error during token issuance: {e}"
            ) from e