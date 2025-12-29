from uuid import UUID, getnode, uuid4
from datetime import datetime, UTC
from dataclasses import dataclass, field
from typing import final

from src.domain.value_objects.wallet_vo import WalletAddressVO


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class WalletLoggedInEvent:
    """Domain event representing a wallet login event in the SIWE authentication system.
    
    This event is raised when a wallet successfully authenticates using SIWE (Sign-In With Ethereum).
    It captures all relevant information about the login event including the wallet address,
    device identifier, and timestamp.
    
    Attributes:
        event_id: Unique identifier for this event instance.
        wallet_address: The wallet address that performed the login as a WalletAddressVO.
        source: Source of the authentication event, defaults to "SIWS".
        device_id: Unique device identifier (MAC address) where the login occurred.
                   Defaults to the MAC address of the current machine.
        logged_in: Timestamp when the login event occurred. Defaults to current UTC time.
    """
    event_id: UUID
    wallet_address: WalletAddressVO
    source: str = "SIWS"
    device_id: int = field(default_factory=lambda: getnode())
    logged_in: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create_event(
        cls,
        pubkey: WalletAddressVO,
        device_id: int | None = None,
    ) -> "WalletLoggedInEvent":
        """Creates a new WalletLoggedInEvent instance.
        
        Factory method for creating a wallet login event with automatically generated
        event ID and timestamp. If device_id is not provided, it will use the MAC
        address of the current machine.
        
        Args:
            pubkey: The wallet address that performed the login as a WalletAddressVO.
            device_id: Optional device identifier (MAC address). If None, uses the
                      MAC address of the current machine via getnode().
        
        Returns:
            A new WalletLoggedInEvent instance with:
            - Automatically generated event_id (UUID v4)
            - Provided wallet address
            - Source set to "SIWS"
            - Device ID (provided or auto-detected)
            - Current UTC timestamp for logged_in
        """
        return cls(
            event_id=uuid4(),
            wallet_address=pubkey,
            source="SIWS",
            device_id=device_id if device_id is not None else getnode(),
            logged_in=datetime.now(UTC),
        )


