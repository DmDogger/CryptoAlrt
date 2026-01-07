import pytest
from datetime import UTC, datetime
from decimal import Decimal

from infrastructures.mappers.price_updated import InfrastructurePriceUpdatedEventMapper
from application.dtos.price_updated import PriceUpdatedEventDTO


class TestInfrastructurePriceUpdatedEventMapper:
    """Tests for InfrastructurePriceUpdatedEventMapper."""

    def test_to_dict(self):
        """Test serialization of PriceUpdatedEventDTO to dict."""
        dto = PriceUpdatedEventDTO(
            cryptocurrency="BTC",
            price=Decimal("50000"),
            timestamp=datetime(2023, 1, 1, tzinfo=UTC),
        )

        mapper = InfrastructurePriceUpdatedEventMapper()
        data = mapper.to_dict(dto)

        assert data["cryptocurrency"] == "BTC"
        assert data["price"] == "50000"
        assert data["timestamp"] == "2023-01-01T00:00:00+00:00"

    def test_from_dict(self):
        """Test deserialization from dict to PriceUpdatedEventDTO."""
        data = {
            "cryptocurrency": "BTC",
            "price": "50000",
            "timestamp": "2023-01-01T00:00:00+00:00",
        }

        mapper = InfrastructurePriceUpdatedEventMapper()
        dto = mapper.from_dict(data)

        assert dto.cryptocurrency == "BTC"
        assert dto.price == Decimal("50000")
        assert dto.timestamp == datetime(2023, 1, 1, tzinfo=UTC)
