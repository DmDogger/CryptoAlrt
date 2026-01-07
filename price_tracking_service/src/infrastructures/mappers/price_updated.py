from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import final

from application.dtos.price_updated import PriceUpdatedEventDTO
from application.interfaces.serialization import SerializationMapperProtocol


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class InfrastructurePriceUpdatedEventMapper(SerializationMapperProtocol):
    """
    Infrastructure mapper for PriceUpdatedEventDTO serialization/deserialization.

    Implements SerializationMapperProtocol to convert PriceUpdatedEventDTO to/from dict
    for external systems (e.g., Kafka).
    """

    def to_dict(self, dto: PriceUpdatedEventDTO) -> dict:
        """
        Converts PriceUpdatedEventDTO to dictionary for serialization.
        """
        return {
            "cryptocurrency": dto.cryptocurrency,
            "price": str(dto.price),
            "timestamp": dto.timestamp.isoformat(),
        }

    def from_dict(self, data: dict) -> PriceUpdatedEventDTO:
        """
        Converts dictionary back to PriceUpdatedEventDTO for deserialization.
        """
        return PriceUpdatedEventDTO(
            cryptocurrency=data["cryptocurrency"],
            price=Decimal(data["price"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )
