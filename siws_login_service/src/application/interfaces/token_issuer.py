from typing import Protocol


class AccessTokenIssuerProtocol(Protocol):
    """Protocol for JWT access token issuer.

    Defines interface for issuing JWT access tokens with configurable
    expiration time and issuer information.
    """

    def issue(
        self,
        sub: str,
        iss: str | None = None,
        ttl: int | None = None,
    ) -> str:
        """Issue a JWT access token for the given subject.

        Creates a JWT token with the specified subject, optional issuer,
        and expiration time.

        Args:
            sub: Subject identifier (typically wallet address or user ID).
            iss: Issuer identifier. Defaults to application default if not provided.
            ttl: Time to live in minutes. Uses default from settings if not provided.

        Returns:
            Encoded JWT token string.

        Raises:
            TokenIssueError: If token encoding fails.
        """
        ...


class RefreshTokenIssuerProtocol(Protocol):
    """Protocol for JWT refresh token issuer.

    Defines interface for issuing JWT refresh tokens with configurable
    expiration time and issuer information.
    """

    def issue(
        self,
        sub: str,
        device_id: str | int,
        iss: str | None = None,
        ttl: int | None = None,
    ) -> str:
        """Issue a JWT refresh token for the given subject.

        Creates a JWT token with the specified subject, optional issuer,
        and expiration time.

        Args:
            sub: Subject identifier (typically wallet address or user ID).
            device_id: User's device ID.
            iss: Issuer identifier. Defaults to application default if not provided.
            ttl: Time to live in minutes. Uses default from settings if not provided.

        Returns:
            Encoded JWT token string.

        Raises:
            TokenIssueError: If token encoding fails.
        """
        ...
