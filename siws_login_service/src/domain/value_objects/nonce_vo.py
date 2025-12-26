from dataclasses import dataclass
from datetime import datetime, UTC
from typing import final
from uuid import uuid4

from domain.exceptions import NonceValidationError


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class NonceVO:
    """Value object representing a nonce for SIWE authentication.
    
    A nonce is a randomized token used to prevent replay attacks in authentication.
    The nonce must be at least 8 alphanumeric characters long.
    
    Attributes:
        value: The nonce string value, must be at least 8 characters long.
    """
    value: str


    def __post_init__(self):
        """Validates that the nonce value meets the minimum length requirement.
        
        Ensures that the nonce is not empty and has at least 8 characters
        as required by the SIWE specification.
        
        Raises:
            NonceValidationError: If the nonce is empty or shorter than 8 characters.
        """
        if not self.value or not len(self.value) >= 8:
            raise NonceValidationError(f"Nonce value must be at least 8 characters long, got {len(self.value) if self.value else 0} characters")


    @classmethod
    def generate(cls) -> "NonceVO":
        """Generates a new random nonce value.
        
        Creates a new NonceVO instance with a randomly generated UUID hex string,
        which provides a cryptographically secure nonce value.
        
        Returns:
            A new NonceVO instance with a randomly generated nonce value.
        """
        return cls(
            value=uuid4().hex
        )