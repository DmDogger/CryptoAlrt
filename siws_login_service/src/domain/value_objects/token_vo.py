from dataclasses import dataclass
from typing import final

from src.domain.exceptions import TokenValidationError


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class TokenPairVO:
    """Value object representing a pair of access and refresh tokens.

    This immutable value object encapsulates both access and refresh tokens,
    ensuring they are non-empty strings through validation.

    Attributes:
        access_token: The access token string used for authentication.
        refresh_token: The refresh token string used to obtain new access tokens.

    Raises:
        TokenValidationError: If either token is empty or not a string type.
    """

    access_token: str
    refresh_token: str

    def __post_init__(self):
        """Validate token values after object initialization.

        Performs validation checks to ensure both tokens are non-empty strings.
        Raises TokenValidationError if validation fails.

        Raises:
            TokenValidationError: If access_token or refresh_token is empty
                or not a string type.
        """
        if not isinstance(self.access_token, str):
            raise TokenValidationError(
                f"Access token must be a string, got {type(self.access_token).__name__} instead"
            )
        if not isinstance(self.refresh_token, str):
            raise TokenValidationError(
                f"Refresh token must be a string, got {type(self.refresh_token).__name__} instead"
            )
        if not self.access_token:
            raise TokenValidationError("Access token must not be empty")
        if not self.refresh_token:
            raise TokenValidationError("Refresh token must not be empty")

        if len(self.access_token.split(".")) != 3:
            raise TokenValidationError(
                "Access token must be a JWT token with 3 parts separated by dots (header.payload.signature)"
            )
        if len(self.refresh_token.split(".")) != 3:
            raise TokenValidationError(
                "Refresh token must be a JWT token with 3 parts separated by dots (header.payload.signature)"
            )

    @classmethod
    def from_string(cls, access_token: str, refresh_token: str) -> "TokenPairVO":
        """Create a TokenPairVO instance from token strings.

        Factory method to create a TokenPairVO from access and refresh token strings.
        The tokens will be validated during object initialization.

        Args:
            access_token: The access token string.
            refresh_token: The refresh token string.

        Returns:
            A new TokenPairVO instance with the provided tokens.

        Raises:
            TokenValidationError: If either token is empty or not a string type.
        """
        return cls(
            access_token=access_token,
            refresh_token=refresh_token,
        )
