from dataclasses import dataclass
from typing import final

import base58

from domain.exceptions import InvalidWalletAddressError


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class WalletAddressVO:
    """Value object representing a wallet address.
    
    Validates that the wallet address is a valid base58-encoded string
    with a decoded length of 32 bytes.
    
    Attributes:
        value: The wallet address as a base58-encoded string.
    """
    value: str

    def __post_init__(self):
        """Validates that the wallet address decodes to exactly 32 bytes.
        
        Raises:
            InvalidWalletAddressError: If the decoded address length is not 32 bytes.
        """
        if not len(base58.b58decode(self.value)) == 32:
            raise InvalidWalletAddressError("Expected wallet address to decode to 32 bytes, but got different length")

    @staticmethod
    def to_bytes(value: str):
        """Converts a base58-encoded wallet address to bytes.
        
        Args:
            value: The base58-encoded wallet address string.
            
        Returns:
            The decoded wallet address as bytes.
        """
        return base58.b58decode(value)

