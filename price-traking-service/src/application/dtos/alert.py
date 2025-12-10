from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import final
from uuid import UUID

from ...domain.value_objects.threshold import ThresholdValueObject


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class AlertDTO:
    """
    Data Transfer Object for Alert entity.

    Used to transfer alert data between application layers without exposing
    domain logic. Contains all necessary fields for alert representation.
    """
    id: UUID
    email: str
    cryptocurrency: str
    threshold_price: ThresholdValueObject
    condition: str
    is_active: bool
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))