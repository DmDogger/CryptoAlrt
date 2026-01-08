"""Portfolio entity representing a collection of cryptocurrency assets."""

from dataclasses import dataclass
from datetime import datetime, UTC
from decimal import Decimal
from typing import final

from domain.entities.asset_entity import AssetEntity
from domain.exceptions import DomainValidationError


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class PortfolioEntity:
    """Entity representing a cryptocurrency portfolio for a wallet.

    This immutable entity contains all assets held in a wallet along with
    portfolio-level metrics like total value, weight, and last update timestamp.

    Attributes:
        wallet_address: Address of the wallet owning this portfolio.
        assets: List of AssetEntity instances in this portfolio.
        total_value: Total USD value of all assets in the portfolio.
        weight: Portfolio weight/percentage in the overall portfolio.
        portfolio_total: Total value of the entire portfolio system.
        updated_at: Timestamp when this portfolio was last updated.
    """

    wallet_address: str
    assets: list[AssetEntity] | None
    total_value: Decimal | None
    weight: Decimal | None
    portfolio_total: Decimal | None
    updated_at: datetime

    def __post_init__(self):
        if not self.wallet_address.strip():
            raise DomainValidationError(f"Wallet Address can't be empty string")

        if not isinstance(self.wallet_address, str):
            raise DomainValidationError(
                f"Wallet address type must be string"
                f"But got: {type(self.wallet_address).__name__}"
            )

        if self.total_value:
            if self.total_value < 0:
                raise DomainValidationError(
                    "Total value of portfolio cannot be negative" f"But got: {self.total_value}"
                )

        if self.weight:
            if self.weight < 0:
                raise DomainValidationError(
                    "Total value of portfolio cannot be negative" f"But got: {self.weight}"
                )

        if datetime.now(UTC) > self.updated_at:
            raise DomainValidationError(
                f"Updated at time must cannot be in the future"
                f"Timestamp now: {datetime.now(UTC)}, time you selected: {self.updated_at}"
            )
