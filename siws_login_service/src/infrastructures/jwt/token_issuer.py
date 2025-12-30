from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import final

import jwt
import structlog

from src.application.interfaces.token_issuer import (
    AccessTokenIssuerProtocol,
    RefreshTokenIssuerProtocol,
)
from src.config.jwt import JWTSettings
from src.infrastructures.exceptions import TokenIssueError

logger = structlog.getLogger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class JWTAccessIssuer(AccessTokenIssuerProtocol):
    """JWT access token issuer.

    Handles creation and encoding of JWT access tokens with configurable
    expiration time and issuer information.
    """

    _jwt_settings: JWTSettings

    def issue(
        self,
        sub: str,
        iss: str | None = None,
        ttl: int | None = None,
    ) -> str:
        """Issue a JWT access token for the given subject.

        Creates a JWT token with the specified subject, optional issuer,
        and expiration time. Uses EdDSA algorithm for signing.

        Args:
            sub: Subject identifier (typically wallet address or user ID).
            iss: Issuer identifier. Defaults to "cryptoalrt.io" if not provided.
            ttl: Time to live in minutes. Uses default from settings if not provided.

        Returns:
            Encoded JWT token string.

        Raises:
            TokenIssueError: If token encoding fails due to PyJWT error.
            TokenIssueError: If unexpected error occurs during token issuance.
        """
        try:
            logger.info(
                "Issuing JWT access token",
                sub=sub,
                iss=iss,
                ttl=ttl,
            )

            exp_time = datetime.now(UTC) + timedelta(
                minutes=ttl if ttl else self._jwt_settings.exp_time_mins
            )

            payload = {
                "sub": sub,
                "typ": "access",
                "exp": exp_time,
                "iss": iss if iss else "cryptoalrt.io",
                "iat": datetime.now(UTC),
            }

            logger.debug(
                "JWT payload created",
                sub=payload.get("sub"),
                type=payload.get("typ"),
                exp=payload.get("exp"),
                iss=payload.get("iss"),
            )

            encoded = jwt.encode(
                payload, self._jwt_settings.secret_key, algorithm="EdDSA"
            )

            logger.info(
                "JWT access token issued successfully",
                sub=sub,
            )
            return encoded

        except jwt.PyJWTError as e:
            logger.error(
                "PyJWT error during access token issuance",
                sub=sub,
                error=str(e),
                exc_info=True,
            )
            raise TokenIssueError(
                f"Failed to issue access token: {e}"
            ) from e

        except Exception as e:
            logger.error(
                "Unexpected error during access token issuance",
                sub=sub,
                error=str(e),
                exc_info=True,
            )
            raise TokenIssueError(
                f"Unexpected error during access token issuance: {e}"
            ) from e


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class JWTRefreshIssuer(RefreshTokenIssuerProtocol):
    """JWT refresh token issuer.

    Handles creation and encoding of JWT refresh tokens with configurable
    expiration time and issuer information.
    """

    _jwt_settings: JWTSettings

    def issue(
        self,
        sub: str,
        iss: str | None = None,
        ttl: int | None = None,
    ) -> str:
        """Issue a JWT refresh token for the given subject.

        Creates a JWT token with the specified subject, optional issuer,
        and expiration time. Uses EdDSA algorithm for signing.

        Args:
            sub: Subject identifier (typically wallet address or user ID).
            iss: Issuer identifier. Defaults to "cryptoalrt.io" if not provided.
            ttl: Time to live in minutes. Uses default from settings if not provided.

        Returns:
            Encoded JWT token string.

        Raises:
            TokenIssueError: If token encoding fails due to PyJWT error.
            TokenIssueError: If unexpected error occurs during token issuance.
        """
        try:
            logger.info(
                "Issuing JWT refresh token",
                sub=sub,
                iss=iss,
                ttl=ttl,
            )

            exp_time = datetime.now(UTC) + timedelta(
                minutes=ttl if ttl else self._jwt_settings.exp_time_mins
            )

            payload = {
                "sub": sub,
                "typ": "refresh",
                "exp": exp_time,
                "iss": iss if iss else "cryptoalrt.io",
                "iat": datetime.now(UTC),
            }

            logger.debug(
                "JWT payload created",
                sub=payload.get("sub"),
                type=payload.get("typ"),
                exp=payload.get("exp"),
                iss=payload.get("iss"),
            )

            encoded = jwt.encode(
                payload, self._jwt_settings.secret_key, algorithm="EdDSA"
            )

            logger.info(
                "JWT refresh token issued successfully",
                sub=sub,
            )
            return encoded

        except jwt.PyJWTError as e:
            logger.error(
                "PyJWT error during refresh token issuance",
                sub=sub,
                error=str(e),
                exc_info=True,
            )
            raise TokenIssueError(
                f"Failed to issue refresh token: {e}"
            ) from e

        except Exception as e:
            logger.error(
                "Unexpected error during refresh token issuance",
                sub=sub,
                error=str(e),
                exc_info=True,
            )
            raise TokenIssueError(
                f"Unexpected error during refresh token issuance: {e}"
            ) from e
