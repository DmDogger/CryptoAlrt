from dataclasses import field, dataclass
from datetime import datetime, UTC
from typing import final
from uuid import UUID

from domain.value_objects.threshold import Threshold

@final
@dataclass(frozen=True, slots=True, kw_only=True)
class AlertDTO:
    """Application DTO for transferring alert data between layers. """
    id: UUID
    email: str
    cryptocurrency: str
    threshold_price: Threshold
    condition: str
    is_active: bool
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))