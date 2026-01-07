from dataclasses import dataclass
from typing import final

import base58

from src.domain.exceptions import InvalidWalletAddressError


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
            raise InvalidWalletAddressError(
                "Expected wallet address to decode to 32 bytes, but got different length"
            )

    @classmethod
    def from_string(cls, value: str) -> "WalletAddressVO":
        """Creates a WalletAddressVO instance from a base58-encoded string.

        Factory method for creating a wallet address value object from a string.
        Validates that the value is a string and that it decodes to exactly 32 bytes.

        Args:
            value: The base58-encoded wallet address string.

        Returns:
            A new WalletAddressVO instance with the provided wallet address value.

        Raises:
            InvalidWalletAddressError: If the value is not a string or if the decoded
                                     address length is not 32 bytes.

        Example:
            >>> wallet_address = WalletAddressVO.from_string("Base58EncodedAddress...")
        """
        if not isinstance(value, str):
            raise InvalidWalletAddressError(f"Wallet address value must be a string")
        return cls(value=value)

    def to_bytes(self) -> bytes:
        """Converts a base58-encoded wallet address to bytes.

        Returns:
            The decoded wallet address as bytes.
        """
        return base58.b58decode(self.value)
