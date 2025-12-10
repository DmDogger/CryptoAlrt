from dataclasses import dataclass
from datetime import UTC
from decimal import Decimal
from typing import final
from uuid import UUID

from ...domain.entities.alert import AlertEntity
from ...domain.value_objects.threshold import ThresholdValueObject
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
            cryptocurrency_id=cryptocurrency_id,
            threshold_price=entity.threshold_price.value,
            condition=entity.condition,
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
            AttributeError: If model.cryptocurrency relationship is not loaded.
                Ensure to use joinedload or selectinload when querying.
        """

        return AlertEntity(
            id=model.id,
            email=model.email,
            cryptocurrency=model.cryptocurrency.symbol,
            threshold_price=ThresholdValueObject(value=model.threshold_price),
            condition=model.condition,
            is_active=model.is_active,
            created_at=model.created_at,
        )

