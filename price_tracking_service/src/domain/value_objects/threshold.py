from dataclasses import dataclass
from decimal import Decimal
from typing import final, Dict

from ..exceptions import DomainValidationError


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class ThresholdValueObject:
    """Value object for price threshold with validation and comparison methods."""
    value: Decimal

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise DomainValidationError("Threshold value must be positive")

    def is_above(self, price: Decimal) -> bool:
        """Check if the given price is above the threshold."""
        return price > self.value

    def is_above_in_percent(self, percent: Decimal):
        return self.value > percent / 100

    def is_below(self, price: Decimal) -> bool:
        """Check if the given price is below the threshold."""
        return price < self.value

    def is_equal(self, price: Decimal) -> bool:
        """Check if the given price equals the threshold."""
        return price == self.value

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {"value": str(self.value)}

    @classmethod
    def from_dict(cls, data: dict) -> "ThresholdValueObject":
        """Deserialize from dictionary."""
        return cls(value=Decimal(data["value"]))

    def __eq__(self, value):
        """Check equality (==) with Decimal or another ThresholdValueObject."""
        if isinstance(value, (int, float, Decimal)):
            return self.value == value
        if isinstance(value, ThresholdValueObject):
            return self.value == value.value
        return False

    def __lt__(self, value):
        """Check less than (<) with Decimal or another ThresholdValueObject."""
        if isinstance(value, (int, float, Decimal)):
            return self.value < value
        if isinstance(value, ThresholdValueObject):
            return self.value < value.value
        return NotImplemented

    def __le__(self, value):
        """Check less than or equal (<=) with Decimal or another ThresholdValueObject."""
        if isinstance(value, (int, float, Decimal)):
            return self.value <= value
        if isinstance(value, ThresholdValueObject):
            return self.value <= value.value
        return NotImplemented

    def __gt__(self, value):
        """Check greater than (>) with Decimal or another ThresholdValueObject."""
        if isinstance(value, (int, float, Decimal)):
            return self.value > value
        if isinstance(value, ThresholdValueObject):
            return self.value > value.value
        return NotImplemented

    def __ge__(self, value):
        """Check greater than or equal (>=) with Decimal or another ThresholdValueObject."""
        if isinstance(value, (int, float, Decimal)):
            return self.value >= value
        if isinstance(value, ThresholdValueObject):
            return self.value >= value.value
        return NotImplemented