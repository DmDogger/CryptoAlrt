from dataclasses import dataclass
from datetime import UTC
from decimal import Decimal
from typing import final
from uuid import UUID

from domain.entities.alert import AlertEntity
from domain.value_objects.threshold import ThresholdValueObject
from ..models.alert import Alert


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class AlertDBMapper:
    """Mapper for converting between AlertEntity and Alert database model."""

    def to_database_model(
        self,
        entity: AlertEntity,
        cryptocurrency_id: UUID,
    ) -> Alert:
        """
        Converts AlertEntity to Alert database model.

        Args:
            entity: The AlertEntity to convert.
            cryptocurrency_id: The UUID of the cryptocurrency (required because
                AlertEntity stores cryptocurrency as string symbol, but Alert model
                requires UUID).

        Returns:
            Alert database model instance.
        """

        return Alert(
            id=entity.id,
            email=entity.email,
            telegram_id=entity.telegram_id,
            cryptocurrency_id=cryptocurrency_id,
            threshold_price=entity.threshold_price,
            is_triggered=entity.is_triggered,
            is_active=entity.is_active,
            created_at=entity.created_at,
        )

    def from_database_model(self, model: Alert) -> AlertEntity:
        """
        Converts Alert database model to AlertEntity.

        Args:
            model: The Alert database model to convert.

        Returns:
            AlertEntity instance.

        Raises:
            ValueError: If cryptocurrency relationship is not loaded.
        """
        if model.cryptocurrency is None:
            raise ValueError("Cryptocurrency relationship must be loaded")
        return AlertEntity(
            id=model.id,
            email=model.email,
            telegram_id=model.telegram_id,
            cryptocurrency=model.cryptocurrency.symbol,
            threshold_price=ThresholdValueObject(value=model.threshold_price),
            is_triggered=model.is_triggered,
            is_active=model.is_active,
            created_at=model.created_at,
        )

    def to_dict(self, model: AlertEntity) -> dict:
        """Convert AlertEntity to dict for database update.
        
        Note: cryptocurrency field is excluded as it's a foreign key (cryptocurrency_id)
        and should not be updated directly through this mapper.
        """
        return {
            "id": model.id,
            "email" : model.email,
            "telegram_id": model.telegram_id,
            "threshold_price": model.threshold_price.value,
            "is_triggered": model.is_triggered,
            "is_active": model.is_active,
            "created_at": model.created_at,
        }

