import pytest
from datetime import datetime, UTC

from uuid import uuid4
from faststream.kafka import TestKafkaBroker
from infrastructures.broker.publisher import KafkaEventPublisher
from application.dtos.price_updated import PriceUpdatedEventDTO

from config.broker import broker_settings
from domain.exceptions import PublishError
from domain.events.price_updated import PriceUpdatedEvent
from infrastructures.consumer.price_update_consumer import (
    consume_price_update_and_check_thresholds,
)


class TestKafkaEventPublisher:
    """Tests for KafkaEventPublisher."""

    @pytest.mark.asyncio
    async def test_handle(self, mock_broker) -> None:
        event_payload = {
            "id": str(uuid4()),
            "cryptocurrency": "bitcoin",
            "name": "Bitcoin",
            "price": "67000.50",
            "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat(),
        }

        async with TestKafkaBroker(mock_broker) as br:
            await br.publish(event_payload, topic=broker_settings.price_updates_topic)

            consume_price_update_and_check_thresholds.mock.assert_called_once()
