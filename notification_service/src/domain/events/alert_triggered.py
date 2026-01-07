from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, final
from uuid import UUID


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class AlertTriggeredEvent:
    """Domain event received when an alert threshold is triggered.

    This immutable event is consumed from Kafka when price_tracking_service
    publishes a threshold triggered notification.

    Note:
        Price fields accept str | int | float because FastStream serializes
        Decimal as numbers, not strings.

    Attributes:
        id: Unique identifier of the event.
        email: Email address of the alert owner.
        telegram_id: Telegram ID of the alert owner (optional).
        alert_id: Unique identifier of the alert that triggered the event.
        cryptocurrency: Symbol of the cryptocurrency that triggered the event.
        current_price: Current price when threshold was triggered.
        threshold_price: The threshold price value that was reached.
        created_at: Timestamp when the event was created.
    """

    id: str
    email: str
    alert_id: str
    cryptocurrency: str
    current_price: str | int | float
    threshold_price: str | int | float
    created_at: str
    telegram_id: int | None = None

    @classmethod
    def from_dict(cls, data: dict) -> AlertTriggeredEvent:
        """Deserialize the event from a dictionary."""
        return cls(
            id=data["id"],
            email=data["email"],
            telegram_id=data.get("telegram_id"),
            alert_id=data["alert_id"],
            cryptocurrency=data["cryptocurrency"],
            current_price=data["current_price"],
            threshold_price=data["threshold_price"],
            created_at=data["created_at"],
        )

    def to_uuid(self) -> UUID:
        """Convert string id to UUID."""
        return UUID(self.id)

    def to_alert_uuid(self) -> UUID:
        """Convert string alert_id to UUID."""
        return UUID(self.alert_id)

    def to_current_price_decimal(self) -> Decimal:
        """Convert current_price to Decimal."""
        return Decimal(str(self.current_price))

    def to_threshold_price_decimal(self) -> Decimal:
        """Convert threshold_price to Decimal."""
        return Decimal(str(self.threshold_price))

    def to_created_at_datetime(self) -> datetime:
        """Convert created_at to datetime."""
        return datetime.fromisoformat(self.created_at)
