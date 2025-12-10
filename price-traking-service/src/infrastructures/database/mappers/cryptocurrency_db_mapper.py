from dataclasses import dataclass
from datetime import UTC
from typing import final

from ...domain.entities.cryptocurrency import CryptocurrencyEntity
from ..models.cryptocurrency import Cryptocurrency


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CryptocurrencyDBMapper:
    """Mapper for converting between CryptocurrencyEntity and Cryptocurrency model."""

    def to_database_model(self, entity: CryptocurrencyEntity) -> Cryptocurrency:
        """Converts CryptocurrencyEntity to Cryptocurrency database model."""
        created_at = entity.created_at
        # Remove timezone info if present, as the model uses naive datetime
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