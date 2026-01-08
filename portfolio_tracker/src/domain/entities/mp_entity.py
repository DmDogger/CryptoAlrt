"""Market price entity representing current cryptocurrency price data."""

from dataclasses import dataclass
from datetime import datetime, UTC
from decimal import Decimal
from typing import final
from uuid import UUID, uuid4

from domain.exceptions import DomainValidationError
from domain.events.price_updated import PriceUpdatedEvent


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class MPEntity:
    """Entity representing market price data for a cryptocurrency.

    This immutable entity contains the current price information for a
    cryptocurrency at a specific timestamp.

    Attributes:
        cryptocurrency: Cryptocurrency ticker symbol (3-10 characters).
        name: Full name of the cryptocurrency.
        price: Current price as Decimal.
        timestamp: Timestamp when the price was recorded.
    """

    id: UUID
    cryptocurrency: str
    name: str
    price: Decimal
    timestamp: datetime

    def __post_init__(self):
        if not (3 <= len(self.cryptocurrency) <= 10):
            raise DomainValidationError(
                "Cryptocurrency's ticker must be between 3 and 10 symbols"
                f"But got: {len(self.cryptocurrency)}"
            )
        if not isinstance(self.price, Decimal):
            raise DomainValidationError(
                "Price of cryptocurrency must be decimal" f"But got: {type(self.price).__name__}"
            )
        if self.timestamp > datetime.now(UTC):
            raise DomainValidationError(
                f"Created at time must cannot be in the future"
                f"Timestamp now: {datetime.now(UTC)}, time you selected: {self.timestamp}"
            )

    @staticmethod
    def from_event(event: PriceUpdatedEvent) -> "MPEntity":
        """Create MPEntity from PriceUpdatedEvent.

        Args:
            event: PriceUpdatedEvent containing cryptocurrency price data.

        Returns:
            A new MPEntity instance created from the event data.
        """
        return MPEntity(
            id=uuid4(),
            cryptocurrency=event.cryptocurrency,
            name=event.name,
            price=event.price,
            timestamp=event.timestamp,
        )
