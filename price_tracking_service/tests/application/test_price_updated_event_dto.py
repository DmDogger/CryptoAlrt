import pytest
from datetime import UTC, datetime
from decimal import Decimal

from src.application.dtos.price_updated import PriceUpdatedEventDTO


class TestPriceUpdatedEventDTO:
    """Tests for PriceUpdatedEventDTO application DTO."""

    def test_create_valid_price_updated_event_dto(self):
        """Test creating a valid PriceUpdatedEventDTO."""
        dto = PriceUpdatedEventDTO(
            cryptocurrency="BTC",
            price=Decimal("50000"),
            timestamp=datetime.now(UTC)
        )

        assert dto.cryptocurrency == "BTC"
        assert dto.price == Decimal("50000")

    def test_price_updated_event_dto_immutable(self):
        """Test that PriceUpdatedEventDTO is immutable."""
        dto = PriceUpdatedEventDTO(
            cryptocurrency="BTC",
            price=Decimal("50000"),
            timestamp=datetime.now(UTC)
        )

        with pytest.raises(AttributeError):
            dto.price = Decimal("51000")