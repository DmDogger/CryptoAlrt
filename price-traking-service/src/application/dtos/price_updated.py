from datetime import datetime
from decimal import Decimal


class PriceUpdatedEventDTO:
    """Application DTO for transferring PriceUpdatedEvent data between layers. """
    cryptocurrency: str
    price: Decimal
    timestamp: datetime