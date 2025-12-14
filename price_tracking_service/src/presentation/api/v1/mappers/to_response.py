from dataclasses import dataclass
from datetime import datetime, UTC
from typing import final
from uuid import uuid4

from domain.entities.alert import AlertEntity
from presentation.api.v1.schemas.alert import AlertResponse, AlertCreateRequest


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class AlertPresentationMapper:
    """
    Mapper for converting between presentation and domain layers.

    Provides methods for converting between Pydantic API models (AlertResponse)
    and domain entities (AlertEntity).
    """
    def from_pydantic_to_entity(
            self,
            pydantic_model: AlertCreateRequest,
    ) -> AlertEntity:
        """
        Convert a Pydantic API model to a domain entity.

        Args:
            pydantic_model: The AlertResponse Pydantic model from the API layer.

        Returns:
            AlertEntity: The corresponding domain entity.
        """
        return AlertEntity(
            id=uuid4(),
            email=pydantic_model.email,
            cryptocurrency=pydantic_model.cryptocurrency_slug,
            threshold_price=pydantic_model.threshold_price,
            is_active=pydantic_model.is_active,
            created_at=datetime.now(UTC),
        )

    def from_entity_to_pydantic(
            self,
            entity: AlertEntity,
    ) -> AlertResponse:
        """
        Convert a domain entity to a Pydantic API model.

        Args:
            entity: The AlertEntity domain entity.

        Returns:
            AlertResponse: The corresponding Pydantic API model for response.
        """
        return AlertResponse(
            id=entity.id,
            email=entity.email,
            cryptocurrency=entity.cryptocurrency,
            threshold_price=entity.threshold_price.value,
            is_active=entity.is_active,
            created_at=entity.created_at,
        )
