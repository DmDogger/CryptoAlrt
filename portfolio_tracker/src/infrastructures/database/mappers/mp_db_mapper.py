"""Mapper for converting between MPEntity and MarketPriceHistory database model."""

from datetime import UTC

from domain.entities.mp_entity import MPEntity
from infrastructures.database.models.cryptoprice import MarketPriceHistory


class MPDBMapper:
    """Mapper for converting between MPEntity and MarketPriceHistory database model."""

    @staticmethod
    def to_database(mp: MPEntity) -> MarketPriceHistory:
        """Convert MPEntity to MarketPriceHistory database model.

        Args:
            mp: MPEntity instance to convert.

        Returns:
            MarketPriceHistory database model instance.
        """
        timestamp = mp.timestamp
        if timestamp.tzinfo is not None:
            timestamp = timestamp.replace(tzinfo=None)

        return MarketPriceHistory(
            id=mp.id,
            cryptocurrency=mp.cryptocurrency,
            name=mp.name,
            price=mp.price,
            timestamp=timestamp,
        )

    @staticmethod
    def from_database(model: MarketPriceHistory) -> MPEntity:
        """Convert MarketPriceHistory database model to MPEntity.

        Args:
            model: MarketPriceHistory database model instance.

        Returns:
            MPEntity instance.
        """
        timestamp = model.timestamp
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)

        return MPEntity(
            id=model.id,
            cryptocurrency=model.cryptocurrency,
            name=model.name,
            price=model.price,
            timestamp=timestamp,
        )

    @staticmethod
    def to_dict(mp: MPEntity) -> dict:
        """Convert MPEntity to dict.

        Args:
            mp: MPEntity instance to convert.

        Returns:
            Dictionary representation of MPEntity.
        """
        return {
            "id": str(mp.id),
            "cryptocurrency": mp.cryptocurrency,
            "name": mp.name,
            "price": str(mp.price),
            "timestamp": mp.timestamp.isoformat(),
        }
