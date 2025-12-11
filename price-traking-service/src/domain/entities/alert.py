from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import final
from uuid import UUID, uuid4
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
    is_active: bool
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", self.email):
            raise DomainValidationError("Invalid email format")
        if len(self.cryptocurrency) < 3 or len(self.cryptocurrency) > 100:
            raise DomainValidationError("Cryptocurrency symbol must be between 3 and 100 characters")

    @classmethod
    def create(
        cls,
        email: str,
        cryptocurrency: str,
        threshold_price: Decimal,
        is_active: bool = True,
    ) -> "AlertEntity":
        """Creates a new AlertEntity instance.

        Args:
            email: User's email.
            cryptocurrency: Cryptocurrency symbol.
            threshold_price: Threshold price value.
            is_active: Whether the alert is active.

        Returns:
            AlertEntity instance.
        """
        return cls(
            id=uuid4(),
            email=email,
            cryptocurrency=cryptocurrency,
            threshold_price=ThresholdValueObject(value=threshold_price),
            is_active=is_active,
            created_at=datetime.now(UTC),
        )





