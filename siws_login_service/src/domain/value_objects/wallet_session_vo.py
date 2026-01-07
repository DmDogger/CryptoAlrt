import uuid
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import final


from src.domain.value_objects.wallet_vo import WalletAddressVO

from src.domain.exceptions import (
    InvalidWalletAddressError,
    DeviceValidationError,
    DateValidationError,
    TokenValidationError,
)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class WalletSessionVO:
    """
    Value Object representing a wallet session.

    Represents a user session with a wallet, including wallet address,
    device identifier, refresh token hash, and revocation status.

    Attributes:
        wallet_address: Wallet address (WalletAddressVO)
        device_id: Device identifier (positive integer)
        refresh_token_hash: Refresh token hash (string with length >= 10)
        is_revoked: Session revocation flag (default: False)
        created_at: Session creation timestamp (cannot be in the future)
    """

    wallet_address: WalletAddressVO
    device_id: str
    refresh_token_hash: str | None
    is_revoked: bool = field(default=False)
    created_at: datetime

    def __post_init__(self):
        """
        Validates object attributes after initialization.

        Validates:
        - Wallet address type and validity
        - Device ID type and positivity
        - Refresh token hash presence and minimum length
        - Created timestamp is not in the future

        Raises:
            InvalidWalletAddressError: If wallet_address is not a WalletAddressVO instance
            DeviceValidationError: If device_id is invalid (not an integer or not positive)
            TokenValidationError: If refresh_token_hash is invalid (empty or too short)
            DateValidationError: If created_at is in the future
        """
        if not isinstance(self.wallet_address, WalletAddressVO):
            raise InvalidWalletAddressError(
                f"Expected wallet_address to be WalletAddressVO, "
                f"but got {type(self.wallet_address).__name__}"
            )
        if not isinstance(self.device_id, str):
            raise DeviceValidationError(
                f"Expected device_id to be a string, "
                f"but got {type(self.device_id).__name__}"
            )

        if self.created_at > datetime.now(UTC):
            raise DateValidationError(
                f"Expected created_at to be in the past or present, "
                f"but got {self.created_at} (future timestamp)"
            )

    def set_hashed_refresh(
        self,
        refresh_token_hash: str,
    ):
        return WalletSessionVO(
            wallet_address=self.wallet_address,
            device_id=self.device_id,
            refresh_token_hash=refresh_token_hash,
            is_revoked=self.is_revoked,
            created_at=self.created_at,
        )

    @classmethod
    def initiate(
        cls,
        wallet_address: WalletAddressVO,
    ) -> "WalletSessionVO":
        """
        Creates a new wallet session.

        Initializes a new session with the current timestamp,
        automatically determines device_id from the device's MAC address,
        and sets is_revoked to False.

        Args:
            wallet_address: Wallet address for session creation

        Returns:
            WalletSessionVO: New wallet session instance

        Raises:
            InvalidWalletAddressError: If wallet_address is invalid
            DeviceValidationError: If device_id is invalid
            TokenValidationError: If refresh_token_hash is invalid
        """
        return cls(
            wallet_address=wallet_address,
            device_id=str(uuid.getnode()),
            refresh_token_hash=None,
            is_revoked=False,
            created_at=datetime.now(UTC),
        )

    def revoke(self) -> "WalletSessionVO":
        """
        Revokes the current wallet session.

        Creates a new session instance with is_revoked flag set to True
        and updated creation timestamp.

        Returns:
            WalletSessionVO: New session instance with revoked status
        """
        return WalletSessionVO(
            wallet_address=self.wallet_address,
            device_id=self.device_id,
            refresh_token_hash=self.refresh_token_hash,
            is_revoked=True,
            created_at=datetime.now(UTC),
        )
