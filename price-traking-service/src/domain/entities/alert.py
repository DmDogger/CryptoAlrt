from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import final
from uuid import UUID
import re

from ..exceptions import DomainValidationError
from ..value_objects.threshold import ThresholdValueObject


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class AlertEntity:
    id: UUID
    email: str
    cryptocurrency: str
    threshold_price: ThresholdValueObject
    condition: str
    is_active: bool
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", self.email):
            raise DomainValidationError("Invalid email format")
        if len(self.cryptocurrency) < 3 or len(self.cryptocurrency) > 100:
            raise DomainValidationError("Cryptocurrency symbol must be between 3 and 100 characters")





