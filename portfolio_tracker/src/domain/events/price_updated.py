"""Domain event representing a cryptocurrency price update."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import final


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class PriceUpdatedEvent:
    """Domain event received when a cryptocurrency price is updated."""

    id: str
    cryptocurrency: str
    name: str = ""
    price: str | int | float | Decimal
    timestamp: str | datetime

    def from_raw(self) -> "PriceUpdatedEvent":
        """Convert price and timestamp to proper types.

        Returns:
            A new PriceUpdatedEvent with Decimal price and ISO format timestamp.
        """
        return PriceUpdatedEvent(
            id=self.id,
            cryptocurrency=self.cryptocurrency,
            name=self.name,
            price=Decimal(self.price),
            timestamp=self.timestamp.isoformat()
        )