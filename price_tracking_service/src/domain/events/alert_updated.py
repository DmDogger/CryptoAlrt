from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, UTC
from decimal import Decimal
from typing import final

from config.event import event_settings


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class AlertUpdatedEvent:
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    alert_id: uuid.UUID
    event_type: str
    email: str
    new_email: str | None = None
    cryptocurrency_symbol_old: str
    cryptocurrency_symbol_new: str | None = None
    old_threshold_price: Decimal
    new_threshold_price: Decimal | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def on_crypto_change(
        cls,
        alert_id: uuid.UUID,
        email: str,
        cryptocurrency_symbol_old: str,
        cryptocurrency_symbol_new: str,
        threshold_price: Decimal,
        created_at: datetime,
    ) -> AlertUpdatedEvent:
        return AlertUpdatedEvent(
            event_id=uuid.uuid4(),
            event_type=event_settings.event_crypto_changed,
            alert_id=alert_id,
            email=email,
            cryptocurrency_symbol_old=cryptocurrency_symbol_old,
            cryptocurrency_symbol_new=cryptocurrency_symbol_new,
            old_threshold_price=threshold_price,
            updated_at=datetime.now(UTC),
            created_at=created_at,
        )

    @classmethod
    def on_email_change(
        cls,
        alert_id: uuid.UUID,
        email: str,
        new_email: str,
        cryptocurrency_symbol: str,
        threshold_price: Decimal,
        created_at: datetime,
    ) -> AlertUpdatedEvent:
        return AlertUpdatedEvent(
            event_id=uuid.uuid4(),
            event_type=event_settings.event_email_changed,
            alert_id=alert_id,
            email=email,
            new_email=new_email,
            cryptocurrency_symbol_old=cryptocurrency_symbol,
            old_threshold_price=threshold_price,
            updated_at=datetime.now(UTC),
            created_at=created_at,
        )

    @classmethod
    def on_threshold_price_change(
        cls,
        alert_id: uuid.UUID,
        email: str,
        cryptocurrency_symbol: str,
        old_threshold_price: Decimal,
        new_threshold_price: Decimal,
        created_at: datetime,
    ) -> AlertUpdatedEvent:
        return AlertUpdatedEvent(
            event_id=uuid.uuid4(),
            event_type=event_settings.event_threshold_changed,
            alert_id=alert_id,
            email=email,
            cryptocurrency_symbol_old=cryptocurrency_symbol,
            old_threshold_price=old_threshold_price,
            new_threshold_price=new_threshold_price,
            updated_at=datetime.now(UTC),
            created_at=created_at,
        )
