from datetime import datetime, UTC

import pytest
from faststream.kafka import TestKafkaBroker
from freezegun import freeze_time

from config.broker import broker_settings
from tests.helpers.mocks import mock_broker
from infrastructures.consumer.alert_triggered_consumer import consume_alert_triggered


class TestAlertTriggeredConsumer:
    @pytest.mark.asyncio
    @freeze_time("30-01-2030 08:00:00")
    async def test_consume_alert_triggered(self, mock_broker: "KafkaBroker"):
        alert_event_payload = {
            "id": "uuid-str",
            "email": "exm@ail.com",
            "alert_id": "alert-uuid",
            "cryptocurrency": "SOL",
            "current_price": "105",
            "threshold_price": "150",
            "created_at": datetime.now(UTC),
            "telegram_id": None,
        }

        async with TestKafkaBroker(mock_broker) as test_kafka_broker:
            await test_kafka_broker.publish(
                alert_event_payload,
                topic=broker_settings.alert_triggered_topic,
            )
            consume_alert_triggered.mock.assert_called_once()
