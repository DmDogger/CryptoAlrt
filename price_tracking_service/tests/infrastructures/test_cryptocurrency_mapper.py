import pytest
from datetime import UTC, datetime
from uuid import uuid4

from infrastructures.mappers.cryptocurrency import InfrastructureCryptocurrencyMapper
from application.dtos.cryptocurrency import CryptocurrencyDTO


class TestInfrastructureCryptocurrencyMapper:
    """Tests for InfrastructureCryptocurrencyMapper."""

    def test_to_dict(self):
        """Test serialization of CryptocurrencyDTO to dict."""
        dto = CryptocurrencyDTO(
            id=uuid4(),
            symbol="BTC",
            name="Bitcoin",
            created_at=datetime(2023, 1, 1, tzinfo=UTC)
        )

        mapper = InfrastructureCryptocurrencyMapper()
        data = mapper.to_dict(dto)

        assert data["id"] == str(dto.id)
        assert data["symbol"] == "BTC"
        assert data["name"] == "Bitcoin"
        assert data["created_at"] == "2023-01-01T00:00:00+00:00"

    def test_from_dict(self):
        """Test deserialization from dict to CryptocurrencyDTO."""
        data = {
            "id": "12345678-1234-5678-9012-123456789012",
            "symbol": "BTC",
            "name": "Bitcoin",
            "created_at": "2023-01-01T00:00:00+00:00"
        }

        mapper = InfrastructureCryptocurrencyMapper()
        dto = mapper.from_dict(data)

        assert str(dto.id) == "12345678-1234-5678-9012-123456789012"
        assert dto.symbol == "BTC"
        assert dto.name == "Bitcoin"
        assert dto.created_at == datetime(2023, 1, 1, tzinfo=UTC)