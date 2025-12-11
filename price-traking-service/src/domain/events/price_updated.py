from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import final


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class PriceUpdatedEvent:
    """Domain event triggered when a cryptocurrency price is updated."""
    cryptocurrency: str
    name: str
    price: Decimal
    timestamp: datetime

    def to_dict(self) -> dict:
        """Serialize the event to a dictionary for external systems (e.g., Kafka)."""
        return {
            "cryptocurrency": self.cryptocurrency,
            "price": str(self.price),  # Decimal to string for JSON
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PriceUpdatedEvent":
        """Deserialize the event from a dictionary."""
        return cls(
            cryptocurrency=data["cryptocurrency"],
            price=Decimal(data["price"]),
            timestamp=datetime.fromisoformat(data["timestamp"])
        )