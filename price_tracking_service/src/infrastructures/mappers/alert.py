from dataclasses import dataclass
from datetime import datetime
from typing import final
from uuid import UUID

from ...application.dtos.alert import AlertDTO
from ...application.interfaces.serialization import SerializationMapperProtocol
from ...domain.value_objects.threshold import ThresholdValueObject


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class InfrastructureAlertMapper(SerializationMapperProtocol):
    """
    Infrastructure mapper for AlertDTO serialization/deserialization.

    Implements SerializationMapperProtocol to convert AlertDTO to/from dict
    for external systems (e.g., Kafka, API responses).
    """

    def to_dict(self, dto: AlertDTO) -> dict:
        """
        Converts AlertDTO to dictionary for serialization.
        """
        return {
            "id": str(dto.id),
            "email": dto.email,
            "cryptocurrency": dto.cryptocurrency,
            "threshold_price": dto.threshold_price.to_dict(),
            "is_active": dto.is_active,
            "created_at": dto.created_at.isoformat(),
        }

    def from_dict(self, data: dict) -> AlertDTO:
        """
        Converts dictionary back to AlertDTO for deserialization.
        """
        return AlertDTO(
            id=UUID(data['id']),
            email=data['email'],
            cryptocurrency=data['cryptocurrency'],
            threshold_price=ThresholdValueObject.from_dict(data['threshold_price']),
            is_active=data['is_active'],
            created_at=datetime.fromisoformat(data['created_at']),
        )


