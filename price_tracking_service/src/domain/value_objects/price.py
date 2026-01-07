from dataclasses import dataclass, field
from datetime import datetime, UTC
from decimal import Decimal
from typing import final

from ..exceptions import DomainValidationError


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class PriceValueObject:
    cryptocurrency: str
    price: Decimal
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self):
        if self.price <= 0:
            raise DomainValidationError("Price must be positive")
        if len(self.cryptocurrency) < 3 or len(self.cryptocurrency) > 100:
            raise DomainValidationError(
                "Cryptocurrency symbol must be between 3 and 100 characters"
            )
        if self.timestamp > datetime.now(UTC):
            raise DomainValidationError("Timestamp can't be in future")

    @staticmethod
    def calculate_change_price_percent_(
        old_price: Decimal,
        new_price: Decimal,
    ):
        return ((new_price - old_price) / old_price) * 100

    def to_dict(self):
        return {
            "cryptocurrency": self.cryptocurrency,
            "price": str(self.price),
            "timestamp": self.timestamp.isoformat(),
        }

    def __eq__(self, other):
        """Serialize to dictionary for external use."""
        if not isinstance(other, (int, float, Decimal)):
            return False
        return other == self.price
