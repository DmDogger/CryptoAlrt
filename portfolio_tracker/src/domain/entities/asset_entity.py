"""Domain entity representing a cryptocurrency asset in a portfolio."""

from datetime import datetime, UTC
from dataclasses import dataclass
from decimal import Decimal
from typing import final
from uuid import UUID, uuid4

from src.domain.exceptions import DomainValidationError


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class AssetEntity:
    """Represents a cryptocurrency asset in a portfolio.

    This entity is immutable and contains all information about a single asset
    held in a wallet, including its ticker symbol, amount, and creation timestamp.

    Attributes:
        asset_id: Unique identifier for the asset entity.
        ticker: Cryptocurrency ticker symbol (3-10 characters).
        amount: Amount of the asset held (must be positive).
        wallet_address: Address of the wallet holding this asset.
        created_at: Timestamp when this asset was added to the portfolio.
    """

    asset_id: UUID
    ticker: str
    amount: Decimal
    wallet_address: str
    created_at: datetime

    def __post_init__(self):
        if len(self.ticker) < 3 and len(self.ticker) < 10:
            raise DomainValidationError(
                f"Ticker's length must be at least 3 sym. and 10 symbols max."
                f"But got: {len(self.ticker)}"
            )
        if not isinstance(self.amount, Decimal):
            raise DomainValidationError(
                f"Asset's amount must be decimal"
                f"But got: {type(self.amount).__name__}"
            )
        if self.amount < 0:
            raise DomainValidationError(
                f"Assets's amount must be greater than 0 and can't be negative"
                f"We got: {self.amount}, when needed more than zero."
            )
        if not self.wallet_address.strip():
            raise DomainValidationError(f"Wallet Address can't be empty string")
        if not isinstance(self.wallet_address, str):
            raise DomainValidationError(
                f"Wallet address type must be string"
                f"But got: {type(self.wallet_address).__name__}"
            )
        if self.created_at > datetime.now(UTC):
            raise DomainValidationError(
                f"Created at time must cannot be in the future"
                f"Timestamp now: {datetime.now(UTC)}, time you selected: {self.created_at}"
            )

    @classmethod
    def create(
        cls,
        ticker: str,
        amount: Decimal,
        wallet_address: str,
        created_at: datetime | None = None,
    ) -> "AssetEntity":
        """Create a new AssetEntity instance.

        Factory method that creates a new asset entity with a generated UUID
        and optional timestamp. If no timestamp is provided, uses current UTC time.

        Args:
            ticker: Cryptocurrency ticker symbol (3-10 characters).
            amount: Amount of the asset (must be positive).
            wallet_address: Address of the wallet holding this asset.
            created_at: Optional timestamp. Defaults to current UTC time.

        Returns:
            A new immutable AssetEntity instance.

        Raises:
            DomainValidationError: If any validation fails (ticker length,
                negative amount, empty wallet address, future timestamp).
        """
        return cls(
            asset_id=uuid4(),
            ticker=ticker,
            amount=amount,
            wallet_address=wallet_address,
            created_at=created_at or datetime.now(UTC),
        )

    def set_amount(self, amount: Decimal) -> "AssetEntity":
        """Create a new AssetEntity with updated amount.

        Since AssetEntity is immutable, this method returns a new instance
        with the same attributes except for the amount.

        Args:
            amount: New amount value (must be positive).

        Returns:
            A new AssetEntity instance with updated amount.

        Raises:
            DomainValidationError: If the new amount is negative or invalid.
        """
        return AssetEntity(
            asset_id=self.asset_id,
            ticker=self.ticker,
            amount=amount,
            wallet_address=self.wallet_address,
            created_at=self.created_at,
        )
