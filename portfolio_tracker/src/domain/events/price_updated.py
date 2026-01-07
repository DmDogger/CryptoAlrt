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

    @classmethod
    def from_raw(cls, data: dict) -> "PriceUpdatedEvent":
        """Convert price and timestamp to proper types.

        Returns:
            A new PriceUpdatedEvent with Decimal price and ISO format timestamp.
        """
        return cls(
            id=str(data["id"]),
            cryptocurrency=str(data["cryptocurrency"]),
            name=str(data.get("name", "")),
            price=Decimal(str(data["price"])),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )
