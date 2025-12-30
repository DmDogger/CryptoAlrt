import base64
import secrets

import pyscrypt
import structlog

from src.application.interfaces.repositories import WalletRepositoryProtocol
from src.application.use_cases.access_token_use_case import AccessTokenIssueUseCase
from src.application.use_cases.refresh_token_use_case import RefreshTokenIssueUseCase
from src.domain.entities.wallet_entity import WalletEntity
from src.domain.exceptions import TokenValidationError
from src.domain.value_objects.token_vo import TokenPairVO
from src.infrastructures.exceptions import InfrastructureError, WalletNotFoundError

logger = structlog.getLogger(__name__)


class TokensIssuerUseCase:
    """Use case for issuing both access and refresh tokens.

    Handles the issuance of JWT access and refresh tokens, hashing the refresh
    token, and updating the wallet entity with the hashed refresh token.
    """

    def __init__(
        self,
        access_issuer_uc: AccessTokenIssueUseCase,
        refresh_issuer_uc: RefreshTokenIssueUseCase,
        wallet_repository: WalletRepositoryProtocol,
    ) -> None:
        """Initialize the use case with required dependencies.

        Args:
            access_issuer_uc: Use case for issuing access tokens.
            refresh_issuer_uc: Use case for issuing refresh tokens.
            wallet_repository: Repository for wallet operations.
        """
        self._access_issuer = access_issuer_uc
        self._refresh_issuer = refresh_issuer_uc
        self._wallet_repository = wallet_repository

    async def execute(
        self,
        wallet_address: str,
    ) -> TokenPairVO:
        """Issue access and refresh tokens for the given wallet address.

        Creates both access and refresh JWT tokens, hashes the refresh token
        using bcrypt, and updates the wallet entity with the hashed refresh token.

        Args:
            wallet_address: The wallet address to issue tokens for.

        Returns:
            TokenPairVO containing both access and refresh tokens.

        Raises:
            WalletNotFoundError: If wallet with the given address is not found.
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

            hashed_bytes = pyscrypt.hash(
                password=refresh_token.encode(),
                salt=secrets.token_bytes(16),
                N=1024,
                r=1,
                p=1,
                dkLen=256
            )

            hashed_refresh = base64.b64encode(hashed_bytes).decode('utf-8')

            logger.info(
                "Tokens issued and hashed successfully, updating wallet",
                wallet_address=wallet_address,
            )

            entity = await self._wallet_repository.get_wallet_by_address(
                wallet_address=wallet_address
            )
            if not entity:
                logger.error(
                    "Wallet not found for token update",
                    wallet_address=wallet_address,
                )
                raise WalletNotFoundError(
                    f"Cannot find wallet to update: {wallet_address}"
                )

            wallet_to_upd = entity.set_hashed_token(hashed_refresh)

            await self._wallet_repository.update_values(
                wallet_address=wallet_address,
                wallet_entity=wallet_to_upd,
            )

            logger.info(
                "Wallet updated successfully with hashed refresh token",
                wallet_address=wallet_address,
            )

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

        except WalletNotFoundError:
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