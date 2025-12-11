from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import final
from uuid import UUID, uuid4


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class AlertCreatedEvent:
    """Domain event triggered when an alert is created due to price change."""

    id: UUID = field(default_factory=uuid4)
    alert_id: UUID
    email: str
    cryptocurrency_id: UUID
    threshold_price: Decimal
    condition: str
    price_change_percent: Decimal
    current_price: Decimal
    timestamp: datetime

    def to_dict(self) -> dict:
        """Serialize the event to a dictionary for external systems (e.g., Kafka)."""
        return {
            "id": str(self.id),
            "alert_id": str(self.alert_id),
            "email": self.email,
            "cryptocurrency_id": self.cryptocurrency_id,
            "threshold_price": str(self.threshold_price),
            "condition": self.condition,
            "price_change_percent": str(self.price_change_percent),
            "current_price": str(self.current_price),
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AlertCreatedEvent":
        """Deserialize the event from a dictionary."""
        return cls(
            id=UUID(data.get("id", uuid4())),
            alert_id=UUID(data["alert_id"]),
            email=data["email"],
            cryptocurrency_id=data["cryptocurrency_id"],
            threshold_price=Decimal(data["threshold_price"]),
            condition=data["condition"],
            price_change_percent=Decimal(data["price_change_percent"]),
            current_price=Decimal(data["current_price"]),
            timestamp=datetime.fromisoformat(data["timestamp"])
        )

