from dataclasses import dataclass
from datetime import datetime, UTC
from typing import final
from uuid import UUID

import base58
from domain.value_objects.wallet_vo import WalletAddressVO
from domain.exceptions import InvalidWalletAddressError, DateValidationError


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class WalletEntity:
    """Entity representing a wallet in the SIWE authentication system.
    
    This entity encapsulates wallet information including the unique identifier,
    wallet address, and timestamps for tracking activity and creation time.
    The entity is immutable (frozen) to ensure data integrity.
    
    Attributes:
        uuid: Unique identifier for the wallet entity.
        wallet_address: The wallet address as a WalletAddressVO value object.
        last_active: Timestamp of the last activity/authentication for this wallet.
        created_at: Timestamp when the wallet entity was first created.
    """
    uuid: UUID
    wallet_address: WalletAddressVO
    last_active: datetime
    created_at: datetime

    def __post_init__(self) -> None:
        """Validates the wallet entity fields.
        
        Ensures that:
        - The wallet_address is a valid WalletAddressVO instance
        - The created_at timestamp is not in the future
        
        Raises:
            InvalidWalletAddressError: If wallet_address is not a WalletAddressVO instance.
            DateValidationError: If created_at is in the future (greater than or equal to current time).
        """
        if not isinstance(self.wallet_address, WalletAddressVO):
            raise InvalidWalletAddressError(
                f"Wallet address must be an instance of WalletAddressVO, "
                f"got {type(self.wallet_address).__name__!r}"
            )
        if self.created_at >= datetime.now(UTC):
            raise DateValidationError(
                f"Created at timestamp cannot be in the future. "
                f"Received: {self.created_at.isoformat()}, "
                f"Current time: {datetime.now(UTC).isoformat()}"
            )

    def ping(self) -> "WalletEntity":
        """Updates the last_active timestamp to the current time.
        
        Since the entity is immutable (frozen dataclass), this method returns
        a new WalletEntity instance with the last_active field set to the current time.
        This is used to track when a wallet was last used for authentication.
        
        Returns:
            A new WalletEntity instance with last_active set to the current timestamp.
        """
        return WalletEntity(
            uuid=self.uuid,
            wallet_address=self.wallet_address,
            last_active=datetime.now(UTC),
            created_at=self.created_at,
        )

    def to_bytes(self) -> bytes:
        """Converts the wallet address to its byte representation.
        
        Decodes the base58-encoded wallet address string into bytes.
        This is useful for cryptographic operations and signature verification.
        
        Returns:
            The wallet address as bytes (32 bytes for Solana addresses).
            
        Raises:
            InvalidWalletAddressError: If the wallet address cannot be decoded from base58.
        """
        try:
            return base58.b58decode(self.wallet_address.value)
        except Exception as e:
            raise InvalidWalletAddressError(
                f"Failed to decode wallet address to bytes: {str(e)}"
            ) from e




