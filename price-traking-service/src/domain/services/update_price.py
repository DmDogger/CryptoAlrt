from datetime import datetime
from decimal import Decimal
from uuid import UUID

from structlog import getLogger

from application.interfaces.repositories import CryptocurrencyRepositoryProtocol
from domain.events.price_updated import PriceUpdatedEvent
from domain.exceptions import CryptocurrencyNotFound

logger = getLogger(__name__)

class PriceUpdateDomainService:
    """Domain service for creating price update events."""

    def __init__(
            self,
            cryptocurrency_repository: CryptocurrencyRepositoryProtocol,
    ):
        """Initialize the domain service with cryptocurrency repository.

        Args:
            cryptocurrency_repository: Repository for accessing cryptocurrency entities.
        """
        self._cryptocurrency_repository = cryptocurrency_repository

    async def create_price_updated_event(
            self,
            cryptocurrency_id: UUID,
            new_price: Decimal,
    ) -> PriceUpdatedEvent:
        """Create a price updated event for the specified cryptocurrency.

        Args:
            cryptocurrency_id: UUID of the cryptocurrency to update.
            new_price: New price value for the cryptocurrency.

        Returns:
            PriceUpdatedEvent: Domain event representing the price update.

        Raises:
            CryptocurrencyNotFound: If cryptocurrency with given ID doesn't exist.
        """
        cryptocurrency = await self._cryptocurrency_repository.get_by_cryptocurrency_id(cryptocurrency_id)
        if cryptocurrency is None:
            raise CryptocurrencyNotFound(f"Cryptocurrency with id: {cryptocurrency_id} not found")
        return PriceUpdatedEvent(
            cryptocurrency=cryptocurrency.symbol,
            name=cryptocurrency.name,
            price=new_price,
            timestamp=datetime.now()
        )




