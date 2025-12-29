from dataclasses import dataclass
from typing import final

from base58 import b58decode

from src.domain.exceptions import SignatureValidationError


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
        if not isinstance(self.value, str):
            raise SignatureValidationError(f"Expected signature type: string, but got :{type(self.value).__name__!r}")


    @classmethod
    def from_string(cls, value: str) -> "SignatureVO":
        """Creates a SignatureVO instance from a base58-encoded string.
        
        Factory method for creating a signature value object from a string.
        Validates that the value is a string and that it decodes to exactly 64 bytes.
        
        Args:
            value: The base58-encoded signature string.
        
        Returns:
            A new SignatureVO instance with the provided signature value.
        
        Raises:
            SignatureValidationError: If the value is not a string or if the decoded
                                    signature length is not 64 bytes.
        
        Example:
            >>> signature = SignatureVO.from_string("Base58EncodedSignature...")
        """
        if not isinstance(value, str):
            raise SignatureValidationError(f"Signature value must be a string")
        return cls(
            value=value,
        )


    def to_bytes(self) -> bytes:
        """Converts a base58-encoded signature to bytes.

        Returns:
            The decoded signature as bytes.
        """
        return b58decode(self.value)
