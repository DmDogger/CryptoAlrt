from dataclasses import dataclass
from datetime import datetime
from typing import final
from uuid import UUID

from ...application.dtos.cryptocurrency import CryptocurrencyDTO
from ...application.interfaces.serialization import SerializationMapperProtocol


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class InfrastructureCryptocurrencyMapper(SerializationMapperProtocol):
    """
    Infrastructure mapper for CryptocurrencyDTO serialization/deserialization.

    Implements SerializationMapperProtocol to convert CryptocurrencyDTO to/from dict
    for external systems (e.g., Kafka, API responses).
    """

    def to_dict(self, dto: CryptocurrencyDTO) -> dict:
        """
        Converts CryptocurrencyDTO to dictionary for serialization.
        """
        return {
            "id": str(dto.id),
            "symbol": dto.symbol,
            "name": dto.name,
            "created_at": dto.created_at.isoformat(),
        }

    def from_dict(self, data: dict) -> CryptocurrencyDTO:
        """
        Converts dictionary back to CryptocurrencyDTO for deserialization.
        """
        return CryptocurrencyDTO(
            id=UUID(data['id']),
            symbol=data['symbol'],
            name=data['name'],
            created_at=datetime.fromisoformat(data['created_at']),
        )

