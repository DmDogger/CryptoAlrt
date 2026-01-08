import sys
import pytest
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

# Mock faststream.kafka before importing publisher
mock_kafka = MagicMock()
sys.modules["faststream.kafka"] = mock_kafka

from infrastructures.broker.publisher import KafkaEventPublisher
from application.dtos.price_updated import PriceUpdatedEventDTO
from domain.exceptions import PublishError


class TestKafkaEventPublisher:
    """Tests for KafkaEventPublisher."""

    @pytest.fixture
    def mock_broker(self):
        """Create a mock Kafka broker."""
        broker = MagicMock()
        broker.publish = AsyncMock()
        return broker

    @pytest.fixture
    def publisher(self, mock_broker):
        """Create KafkaEventPublisher instance with mock broker."""
        return KafkaEventPublisher(broker=mock_broker)

    @pytest.fixture
    def price_updated_dto(self):
        """Create a sample PriceUpdatedEventDTO."""
        return PriceUpdatedEventDTO(
            cryptocurrency="BTC",
            price=Decimal("50000"),
            timestamp=datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC),
        )

    @pytest.mark.asyncio
    async def test_publish_success(self, publisher, mock_broker, price_updated_dto):
        """Test successful event publishing."""
        topic = "price-updates"

        await publisher.publish(topic=topic, event=price_updated_dto)

        mock_broker.publish.assert_called_once_with(message=price_updated_dto, topic=topic)

    @pytest.mark.asyncio
    async def test_publish_with_different_topic(self, publisher, mock_broker, price_updated_dto):
        """Test publishing to different topic."""
        topic = "alert-created"

        await publisher.publish(topic=topic, event=price_updated_dto)

        mock_broker.publish.assert_called_once_with(message=price_updated_dto, topic=topic)

    @pytest.mark.asyncio
    async def test_publish_with_different_event_type(self, publisher, mock_broker):
        """Test publishing different event types."""
        from application.dtos.alert import AlertDTO
        from domain.value_objects.threshold import ThresholdValueObject

        alert_dto = AlertDTO(
            id=uuid4(),
            email="user@example.com",
            cryptocurrency="BTC",
            threshold_price=ThresholdValueObject(value=Decimal("50000")),
            is_active=True,
            created_at=datetime(2023, 1, 1, tzinfo=UTC),
        )

        await publisher.publish(topic="alerts", event=alert_dto)

        mock_broker.publish.assert_called_once_with(message=alert_dto, topic="alerts")

    @pytest.mark.asyncio
    async def test_publish_raises_error_on_failure(self, publisher, mock_broker, price_updated_dto):
        """Test that PublishError is raised when publishing fails."""
        mock_broker.publish.side_effect = Exception("Kafka connection error")
        topic = "price-updates"

        with pytest.raises(PublishError, match="Failed to publish event"):
            await publisher.publish(topic=topic, event=price_updated_dto)

        mock_broker.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_with_dict_event(self, publisher, mock_broker):
        """Test publishing a dictionary event."""
        event_dict = {
            "cryptocurrency": "BTC",
            "price": "50000",
            "timestamp": "2023-01-01T12:00:00+00:00",
        }

        await publisher.publish(topic="price-updates", event=event_dict)

        mock_broker.publish.assert_called_once_with(message=event_dict, topic="price-updates")
