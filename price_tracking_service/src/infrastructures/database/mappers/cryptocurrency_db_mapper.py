from dataclasses import dataclass
from datetime import UTC, datetime
from typing import final
from uuid import UUID, uuid4

from src.domain.entities.cryptocurrency import CryptocurrencyEntity
from src.application.dtos.coingecko_object import CoinGeckoDTO
from src.infrastructures.database.models.cryptocurrency import Cryptocurrency, CryptocurrencyPrice


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CryptocurrencyDBMapper:
    """Mapper for converting between CryptocurrencyEntity and Cryptocurrency model."""

    def to_database_model(self, entity: CryptocurrencyEntity) -> Cryptocurrency:
        """Converts CryptocurrencyEntity to Cryptocurrency database model."""
        created_at = entity.created_at
        if created_at.tzinfo is not None:
            created_at = created_at.replace(tzinfo=None)
        
        return Cryptocurrency(
            id=entity.id,
            symbol=entity.symbol,
            name=entity.name,
            created_at=created_at,
        )

    def from_database_model(self, model: Cryptocurrency) -> CryptocurrencyEntity:
        """Converts Cryptocurrency database model to CryptocurrencyEntity."""
        created_at = model.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)
        
        return CryptocurrencyEntity(
            id=model.id,
            symbol=model.symbol,
            name=model.name,
            created_at=created_at,
        )



    def from_api_response_to_database_model(
            self,
            entity: CoinGeckoDTO,
            cryptocurrency_id: UUID
    ) -> CryptocurrencyPrice:
        """Converts CoinGeckoDTO to CryptocurrencyPrice database model.
        
        Args:
            entity: CoinGeckoDTO with price data from API.
            cryptocurrency_id: UUID of the cryptocurrency (aggregate root).
        
        Returns:
            CryptocurrencyPrice database model instance.
        """
        return CryptocurrencyPrice(
            id=uuid4(),
            cryptocurrency_id=cryptocurrency_id,
            price_usd=entity.current_price,
            timestamp=datetime.now(UTC),
            market_cap_usd=entity.market_cap,
            total_volume_24h_usd=entity.total_volume,
            high_24h=entity.high_24h,
            low_24h=entity.low_24h,
            price_change_24h=entity.price_change_24h,
            price_change_percentage_24h=entity.price_change_percentage_24h,
        )
