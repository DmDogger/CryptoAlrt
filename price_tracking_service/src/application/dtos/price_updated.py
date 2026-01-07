from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import final


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class PriceUpdatedEventDTO:
    """
    Data Transfer Object for PriceUpdatedEvent.

    Used to transfer price update data between application layers
    without exposing domain logic.
    """

    cryptocurrency: str
    price: Decimal
    timestamp: datetime
