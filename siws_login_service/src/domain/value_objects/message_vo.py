from datetime import datetime, UTC
from dataclasses import dataclass, field
from typing import final

import base58
from domain.value_objects.wallet_vo import WalletAddressVO

from domain.exceptions import DateValidationError, InvalidWalletAddressError


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class MessageVO:
    """Value object representing a SIWE (Sign-In With Ethereum) message for Solana.
    
    This class encapsulates all the fields required for a SIWE authentication message,
    following the SIWE specification adapted for Solana blockchain.
    
    Attributes:
        wallet_address: Solana address performing the signing.
        domain: RFC 4501 DNS authority that is requesting the signing.
        statement: Human-readable ASCII assertion that the user will sign, must not contain newline characters.
        uri: RFC 3986 URI referring to the resource that is the subject of the signing.
        version: Current version of the message.
        nonce: Randomized token used to prevent replay attacks, at least 8 alphanumeric characters.
        expiration_time: ISO 8601 datetime string indicating when the signed message expires.
        issued_at: ISO 8601 datetime string of the current time when the message was issued.
        chain_id: Chain ID to which the session is bound, and the network where Contract Accounts must be resolved.
    """
    wallet_address: WalletAddressVO # Solana address performing the signing */
    domain: str # RFC 4501 dns authority that is requesting the signing.
    statement: str | None # Human-readable ASCII assertion that the user will sign, and it must not contain newline characters.
    uri: str # RFC 3986 URI referring to the resource that is the subject of the signing
    version: str | None # Current version of the message.
    nonce: "NonceVO" # Randomized token used to prevent replay attacks, at least 8 alphanumeric
    expiration_time: datetime # ISO 8601 datetime string that, if present, indicates when the signed
    issued_at: datetime = field(default_factory=lambda: datetime.now(UTC)) # ISO 8601 datetime string of the current time.
    chain_id: str = "mainnet-beta" # Chain ID to which the session is bound, and the network where Contract Accounts must be resolved.

    def __post_init__(self):
        """Validates that the issued_at time is before the expiration_time.
        
        Ensures that the message has a valid time range where the issue time
        is strictly before the expiration time.
        
        Raises:
            DateValidationError: If issued_at is greater than or equal to expiration_time.
        """
        if self.issued_at >= self.expiration_time:
            raise DateValidationError(f"issued_at ({self.issued_at}) must be before expiration_time ({self.expiration_time}).")
        if not isinstance(self.wallet_address, WalletAddressVO):
            raise InvalidWalletAddressError(f"Wallet must be an instance of Wallet Address Value Object.")



    @classmethod
    def from_record(cls, record: "NonceVO") -> "MessageVO":
        """Creates a MessageVO instance from a NonceVO record.
        
        Args:
            record: The NonceVO record containing message data.
            
        Returns:
            A new MessageVO instance constructed from the record data.
        """
        return cls(
            wallet_address=record.wallet_address,
            domain=record.domain,
            statement=record.statement,
            uri=record.uri,
            version=record.version,
            chain_id=record.chain_id,
            nonce=record.value,
            expiration_time=record.expiration_time,
        )

    def to_string(self) -> str:
        """Converts the message to a formatted string representation.
        
        Formats the message according to SIWE specification, including all required
        fields in a human-readable format suitable for user signing.
        
        Returns:
            A formatted string representation of the message ready for signing.
        """
        statement_block = f"{self.statement}\n\n" if self.statement else ""

        return (
            f"{self.domain} wants you to sign in with your Solana account:\n"
            f"{self.wallet_address}\n"
            f"\n"
            f"{statement_block}"
            f"URI: {self.uri}\n"
            f"Version: {self.version}\n"
            f"Chain ID: {self.chain_id}\n"
            f"Nonce: {self.nonce}\n"
            f"Issued At: {self.issued_at.strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
            f"Expiration Time: {self.expiration_time.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        )






