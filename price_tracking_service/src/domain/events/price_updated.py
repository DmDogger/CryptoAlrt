from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import final
from uuid import UUID, uuid4


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class PriceUpdatedEvent:
    """Domain event triggered when a cryptocurrency price is updated."""

    id: UUID = field(default_factory=uuid4)
    cryptocurrency: str
    name: str = ""
    price: Decimal
    timestamp: datetime

    def to_dict(self) -> dict:
        """Serialize the event to a dictionary for external systems (e.g., Kafka)."""
        timestamp_naive = (
            self.timestamp.replace(tzinfo=None) if self.timestamp.tzinfo else self.timestamp
        )
        return {
            "id": str(self.id),
            "cryptocurrency": self.cryptocurrency,
            "name": self.name,
            "price": str(self.price),
            "timestamp": timestamp_naive.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PriceUpdatedEvent":
        """Deserialize the event from a dictionary."""
        return cls(
            id=UUID(data["id"]) if "id" in data and data["id"] else uuid4(),
            cryptocurrency=data["cryptocurrency"],
            name=data.get("name", ""),
            price=Decimal(data["price"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )
