from dataclasses import dataclass
from typing import final

from base58 import b58decode

from domain.exceptions import SignatureValidationError


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class SignatureVO:
    """Value object representing a cryptographic signature.
    
    Validates that the signature is a valid base58-encoded string
    with a decoded length of 64 bytes (512 bits), which is the standard
    length for Ed25519 signatures used in Solana.
    
    Attributes:
        value: The signature as a base58-encoded string.
    """
    value: str

    def __post_init__(self):
        """Validates that the signature decodes to exactly 64 bytes.
        
        Ensures that the signature has the correct length for Ed25519 signatures
        used in Solana blockchain (64 bytes = 512 bits).
        
        Raises:
            SignatureValidationError: If the decoded signature length is not 64 bytes.
        """
        if not len(b58decode(self.value)) == 64:
            raise SignatureValidationError(f"Expected signature to decode to 64 bytes, but got {len(b58decode(self.value))} bytes")

    @staticmethod
    def to_bytes(value: str) -> bytes:
        """Converts a base58-encoded signature to bytes.
        
        Args:
            value: The base58-encoded signature string.
            
        Returns:
            The decoded signature as bytes.
        """
        return b58decode(value)
