import pytest
from datetime import UTC, datetime
from decimal import Decimal

from domain.events.price_updated import PriceUpdatedEvent


class TestPriceUpdatedEvent:
    """Tests for PriceUpdatedEvent domain event."""

    def test_create_valid_event(self):
        """Test creating a valid price updated event."""
        timestamp = datetime.now(UTC)
        event = PriceUpdatedEvent(
            cryptocurrency="BTC", price=Decimal("50000"), timestamp=timestamp
        )

        assert event.cryptocurrency == "BTC"
        assert event.price == Decimal("50000")
        assert event.timestamp == timestamp

    def test_event_to_dict(self):
        """Test serialization to dict."""
        timestamp = datetime(2023, 1, 1, tzinfo=UTC)
        event = PriceUpdatedEvent(
            cryptocurrency="BTC", price=Decimal("50000"), timestamp=timestamp
        )

        data = event.to_dict()
        assert "id" in data
        assert data["cryptocurrency"] == "BTC"
        assert data["name"] == ""  # Default value
        assert data["price"] == "50000"
        # to_dict() removes timezone, so we compare without timezone
        assert data["timestamp"] == timestamp.replace(tzinfo=None).isoformat()

    def test_event_from_dict(self):
        """Test deserialization from dict."""
        timestamp_str = "2023-01-01T00:00:00+00:00"
        data = {"cryptocurrency": "BTC", "price": "50000", "timestamp": timestamp_str}

        event = PriceUpdatedEvent.from_dict(data)
        assert event.id is not None  # Should be generated
        assert event.cryptocurrency == "BTC"
        assert event.name == ""  # Default value
        assert event.price == Decimal("50000")
        assert event.timestamp == datetime.fromisoformat(timestamp_str)

    def test_event_immutable(self):
        """Test that PriceUpdatedEvent is immutable."""
        event = PriceUpdatedEvent(
            cryptocurrency="BTC", price=Decimal("50000"), timestamp=datetime.now(UTC)
        )

        with pytest.raises(AttributeError):
            event.price = Decimal("51000")
