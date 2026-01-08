from datetime import datetime, UTC, timedelta
from uuid import uuid4, UUID

from dataclasses import dataclass, field
from typing import final

from src.domain.value_objects.wallet_vo import WalletAddressVO
from src.domain.value_objects.nonce_vo import NonceVO

from src.domain.exceptions import (
    NonceValidationError,
    InvalidWalletAddressError,
    DateValidationError,
    DomainError,
    NonceAlreadyUsedError,
)
from src.domain.value_objects.message_vo import MessageVO


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class NonceEntity:
    """Entity representing a nonce record for SIWE authentication.

    This entity encapsulates all the information needed for a SIWE authentication
    session, including the nonce value, wallet address, domain, and timing information.
    It tracks whether the nonce has been used and whether it has expired.

    Attributes:
        uuid: Unique identifier for the nonce record.
        wallet_address: Solana address performing the signing.
        nonce: Randomized token used to prevent replay attacks, at least 8 alphanumeric characters.
        domain: RFC 4501 DNS authority that is requesting the signing.
        statement: Human-readable ASCII assertion that the user will sign, must not contain newline characters.
        uri: RFC 3986 URI referring to the resource that is the subject of the signing.
        version: Current version of the message.
        expiration_time: ISO 8601 datetime string indicating when the signed message expires.
        used_at: Timestamp when the nonce was used, None if not yet used.
        issued_at: ISO 8601 datetime string of the current time when the message was issued.
        chain_id: Chain ID to which the session is bound, and the network where Contract Accounts must be resolved.
    """

    uuid: UUID
    wallet_address: WalletAddressVO
    nonce: NonceVO  # Randomized token used to prevent replay attacks, at least 8 alphanumeric
    domain: str = "cryptoalrt.io"  # RFC 4501 dns authority that is requesting the signing.
    statement: (
        str | None
    )  # Human-readable ASCII assertion that the user will sign, and it must not contain newline characters.
    uri: str  # RFC 3986 URI referring to the resource that is the subject of the signing
    version: str | None  # Current version of the message.
    expiration_time: (
        datetime  # ISO 8601 datetime string that, if present, indicates when the signed
    )
    used_at: datetime | None = field(default=None)
    issued_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )  # ISO 8601 datetime string of the current time.
    chain_id: str = (
        "mainnet-beta"  # Chain ID to which the session is bound, and the network where Contract Accounts must be resolved.
    )

    def __post_init__(self):
        """Validates the nonce entity fields.

        Ensures that:
        - The nonce is a valid NonceVO instance
        - The wallet address is a valid WalletAddressVO instance
        - The issued_at time is before the expiration_time

        Raises:
            NonceValidationError: If the nonce is not a valid NonceVO instance.
            InvalidWalletAddressError: If the wallet address is not a valid WalletAddressVO instance.
            DateValidationError: If issued_at is greater than or equal to expiration_time.
        """
        if not isinstance(self.nonce, NonceVO):
            raise NonceValidationError(
                f"Nonce must be an instance of NonceVO, got {type(self.nonce).__name__}"
            )
        if not isinstance(self.wallet_address, WalletAddressVO):
            raise InvalidWalletAddressError(
                f"Wallet address must be an instance of WalletAddressVO, got {type(self.wallet_address).__name__}"
            )
        if not isinstance(self.statement, str):
            raise DomainError(f"Statement must be a string, got {type(self.statement).__name__}")
        if self.issued_at >= self.expiration_time:
            raise DateValidationError(
                f"issued_at ({self.issued_at}) must be before expiration_time ({self.expiration_time})"
            )

    @classmethod
    def create(
        cls,
        wallet_address: WalletAddressVO,
        nonce: NonceVO,
        statement: str,
        uri: str | None = None,
        version: str | None = None,
        expiration_time: datetime | None = None,
        ttl_time: int = 59,
    ) -> "NonceEntity":
        """Creates a new NonceEntity instance with default values for optional fields.

        Factory method for creating a nonce entity with automatically generated UUID
        and sensible defaults for domain, URI, version, and expiration time.

        Args:
            wallet_address: Solana address performing the signing as a WalletAddressVO.
            nonce: Randomized token used to prevent replay attacks as a NonceVO.
            statement: Human-readable ASCII assertion that the user will sign.
            uri: Optional RFC 3986 URI. If None, defaults to "https://cryptoalrt.io/login/solana".
            version: Optional message version. If None, defaults to "1".
            expiration_time: Optional expiration datetime. If None, defaults to current time + ttl_time minutes.
            ttl_time: Time to live in minutes for expiration time calculation. Defaults to 59 minutes.

        Returns:
            A new NonceEntity instance with:
            - Automatically generated UUID (UUID v4)
            - Provided wallet address and nonce
            - Domain set to "cryptoalrt.io"
            - Provided statement
            - URI (provided or default)
            - Version (provided or default "1")
            - Expiration time (provided or calculated from ttl_time)
            - used_at set to None (not used)
            - issued_at set to current UTC time
            - chain_id set to "mainnet-beta"

        Raises:
            NonceValidationError: If the nonce is not a valid NonceVO instance.
            InvalidWalletAddressError: If the wallet address is not a valid WalletAddressVO instance.
            DateValidationError: If expiration_time is before issued_at.
        """
        return cls(
            uuid=uuid4(),
            wallet_address=wallet_address,
            nonce=nonce,
            domain="cryptoalrt.io",
            statement=statement,
            uri=uri if uri is not None else "https://cryptoalrt.io/login/solana",
            version=version if version is not None else "1",
            expiration_time=(
                expiration_time
                if expiration_time is not None
                else datetime.now(UTC) + timedelta(minutes=ttl_time)
            ),
            used_at=None,
            issued_at=datetime.now(UTC),
            chain_id="mainnet-beta",
        )

    def is_expired(self) -> bool:
        """Checks if the nonce has expired.

        Returns:
            True if the current time is greater than or equal to the expiration time, False otherwise.
        """
        return datetime.now(UTC) >= self.expiration_time

    def is_used(self) -> bool:
        """Checks if the nonce has been used.

        Returns:
            True if the nonce has been marked as used (used_at is not None), False otherwise.
        """
        return self.used_at is not None

    def convert_to_message_vo(self) -> MessageVO:
        """Converts the nonce entity to a MessageVO value object.

        Creates a MessageVO instance from the nonce entity's data,
        which can be used for generating the message string that users will sign.

        Returns:
            A MessageVO instance containing all the message data from this entity.
        """
        return MessageVO(
            wallet_address=self.wallet_address,  # Solana address performing the signing
            domain=self.domain,  # RFC 4501 dns authority that is requesting the signing.
            statement=self.statement,  # Human-readable ASCII assertion that the user will sign, and it must not contain newline characters.
            uri=self.uri,  # RFC 3986 URI referring to the resource that is the subject of the signing
            version=self.version,  # Current version of the message.
            nonce=self.nonce,  # Randomized token used to prevent replay attacks, at least 8 alphanumeric
            expiration_time=self.expiration_time,  # ISO 8601 datetime string that, if present, indicates when the signed
            issued_at=self.issued_at,
            chain_id=self.chain_id,
        )

    def mark_as_used(self) -> "NonceEntity":
        """Marks the nonce as used by creating a new entity with used_at timestamp.

        Since the entity is immutable (frozen dataclass), this method returns
        a new NonceEntity instance with the used_at field set to the current time.

        Returns:
            A new NonceEntity instance with used_at set to the current timestamp.

        Raises:
            NonceAlreadyUsedError: If the nonce is already used.
        """
        if self.used_at is not None:
            raise NonceAlreadyUsedError(f"Nonce is already marked as used.")
        return NonceEntity(
            uuid=self.uuid,
            wallet_address=self.wallet_address,
            nonce=self.nonce,
            domain=self.domain,
            statement=self.statement,
            uri=self.uri,
            version=self.version,
            expiration_time=self.expiration_time,
            issued_at=self.issued_at,
            chain_id=self.chain_id,
            used_at=datetime.now(UTC),
        )
