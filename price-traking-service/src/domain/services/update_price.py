from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.domain.events.price_updated import PriceUpdatedEvent


class PriceUpdateDomainService:
    """Domain service for creating price update events."""

    @staticmethod
    async def create_price_updated_event(
            cryptocurrency_id: UUID,
            cryptocurrency_symbol: str,
            cryptocurrency_name: str,
            new_price: Decimal,
    ) -> PriceUpdatedEvent:
        """Create a price updated event for the specified cryptocurrency.

        Args:
            cryptocurrency_id: UUID of the cryptocurrency to update.
            cryptocurrency_symbol: Symbol of the cryptocurrency (e.g., 'BTC').
            cryptocurrency_name: Name of the cryptocurrency (e.g., 'Bitcoin').
            new_price: New price value for the cryptocurrency.

        Returns:
            PriceUpdatedEvent: Domain event representing the price update.
        """
        return PriceUpdatedEvent(
            id=cryptocurrency_id,
            cryptocurrency=cryptocurrency_symbol,
            name=cryptocurrency_name,
            price=new_price,
            timestamp=datetime.now()
        )




