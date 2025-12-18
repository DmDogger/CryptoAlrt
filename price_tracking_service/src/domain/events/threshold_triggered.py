from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, UTC
from decimal import Decimal
from typing import final


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class ThresholdTriggeredEvent:
    """Domain event triggered when a cryptocurrency price reaches its threshold.
    
    This immutable event is published when the alert threshold condition is met,
    signaling that the cryptocurrency price has reached or exceeded the defined threshold.
    
    Attributes:
        id: Unique identifier of the event.
        email: Email address of the alert owner.
        alert_id: Unique identifier of the alert that triggered the event.
        cryptocurrency: Symbol of the cryptocurrency that triggered the event.
        current_price: Current price of the cryptocurrency when threshold was triggered.
        threshold_price: The threshold price value that was reached.
        created_at: Timestamp when the event was created in UTC.
    """
    id: uuid.UUID
    email: str
    telegram_id: int | None
    alert_id: uuid.UUID
    cryptocurrency: str
    current_price: Decimal
    threshold_price: Decimal
    created_at: datetime

    @classmethod
    def create(
            cls,
            email: str,
            telegram_id: int | None,
            cryptocurrency: str,
            threshold_price: Decimal,
            alert_id: uuid.UUID,
            current_price: Decimal,
    ) -> ThresholdTriggeredEvent:
        """Factory method for creating a new ThresholdTriggeredEvent.
        
        Args:
            email: Email address of the alert owner.
            cryptocurrency: Symbol of the cryptocurrency (e.g., BTC, ETH).
            threshold_price: The threshold price value that was reached.
            alert_id: Identification of alert.
            current_price: Current price of the cryptocurrency when threshold was triggered.
            
        Returns:
            New ThresholdTriggeredEvent instance with auto-generated ID and current timestamp.
        """
        return cls(
            id=uuid.uuid4(),
            email=email,
            telegram_id=telegram_id,
            current_price=current_price,
            alert_id=alert_id,
            cryptocurrency=cryptocurrency,
            threshold_price=threshold_price,
            created_at=datetime.now(UTC)
        )

    def to_dict(self) -> dict:
        """Serialize the event to a dictionary for external systems (e.g., Kafka).
        
        Returns:
            Dictionary representation of the event with serialized values.
        """
        return {
            "id": str(self.id),
            "email": self.email,
            "telegram_id": self.telegram_id,
            "alert_id": str(self.alert_id),
            "cryptocurrency": self.cryptocurrency,
            "current_price": str(self.current_price),
            "threshold_price": str(self.threshold_price),
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> ThresholdTriggeredEvent:
        """Deserialize the event from a dictionary.
        
        Args:
            data: Dictionary containing event data.
            
        Returns:
            ThresholdTriggeredEvent instance reconstructed from dictionary.
        """
        return cls(
            id=uuid.UUID(data.get("id", uuid.uuid4())),
            email=data["email"],
            telegram_id=data.get("telegram_id"),
            alert_id=uuid.UUID(data["alert_id"]),
            cryptocurrency=data["cryptocurrency"],
            current_price=Decimal(data["current_price"]),
            threshold_price=Decimal(data["threshold_price"]),
            created_at=datetime.fromisoformat(data["created_at"])
        )




