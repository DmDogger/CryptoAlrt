from dataclasses import dataclass
from decimal import Decimal
from typing import final

from domain.exceptions import DomainValidationError


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class AnalyticsValueObject:
    ticker: str
    position_value: Decimal | None
    allocation: Decimal | None
    port_change: Decimal | None
    amount: Decimal | None = None
    current_price: Decimal | None = None

    def __post_init__(self):
        if not self.ticker or not self.ticker.strip():
            raise DomainValidationError("Ticker cannot be empty or whitespace")

        if len(self.ticker.strip()) < 3:
            raise DomainValidationError("Ticker must be at least 3 characters long")

        if self.position_value is not None and self.position_value < 0:
            raise DomainValidationError("Position value cannot be negative")

        if self.allocation is not None and self.allocation < 0:
            raise DomainValidationError("Allocation cannot be negative")

        if self.amount is not None and self.amount < 0:
            raise DomainValidationError("Amount cannot be negative")

        if self.current_price is not None and self.current_price < 0:
            raise DomainValidationError("Current price cannot be negative")

    @classmethod
    def create(
        cls,
        ticker: str,
        position_value: Decimal | None = None,
        allocation: Decimal | None = None,
        port_change: Decimal | None = None,
        amount: Decimal | None = None,
        current_price: Decimal | None = None,
    ) -> "AnalyticsValueObject":
        return cls(
            ticker=ticker,
            position_value=position_value if position_value else None,
            allocation=allocation if allocation else None,
            port_change=port_change if port_change else None,
            amount=amount if amount else None,
            current_price=current_price if current_price else None,
        )
