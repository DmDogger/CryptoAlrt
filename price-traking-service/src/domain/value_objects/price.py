from dataclasses import dataclass, field
from datetime import datetime, UTC
from decimal import Decimal
from typing import final

from ..exceptions import DomainValidationError

@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Price:
    cryptocurrency: str
    price: Decimal
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self):
        if self.price < 0:
            raise DomainValidationError("Price cannot be below than zero")
        if len(self.cryptocurrency) < 3 or len(self.cryptocurrency) > 100:
            raise DomainValidationError("Cryptocurrency symbol must be between 3 and 100 characters")
        if self.timestamp > datetime.now(UTC):
            raise DomainValidationError("Timestamp can't be in future")

    def to_dict(self):
        return {
            'cryptocurrency': self.cryptocurrency,
            'price': self.price,
            'timestamp': self.timestamp,
        }

    def __eq__(self, other):
        """Serialize to dictionary for external use."""
        if not isinstance(other, (int, float, Decimal)):
            return False
        return other == self.price




