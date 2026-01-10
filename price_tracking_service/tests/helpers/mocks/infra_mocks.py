from unittest.mock import MagicMock

import pytest
from dishka import make_async_container
from dishka.integrations.faststream import setup_dishka as setup_dishka_faststream
from faststream.kafka.annotations import KafkaBroker

from tests.helpers.providers.use_cases import MockUseCasesProvider

from config.broker import broker_settings
from infrastructures.consumer.price_update_consumer import (
    consume_price_update_and_check_thresholds,
)


@pytest.fixture
def container():
    container = make_async_container(MockUseCasesProvider())
    yield container


@pytest.fixture
def mock_broker(container):
    broker = KafkaBroker(bootstrap_servers=MagicMock())

    setup_dishka_faststream(container, broker=broker, auto_inject=True)

    broker.subscriber(
        broker_settings.price_updates_topic,
        title="consume_price_update_and_check_threshold",
    )(consume_price_update_and_check_thresholds)

    return broker
