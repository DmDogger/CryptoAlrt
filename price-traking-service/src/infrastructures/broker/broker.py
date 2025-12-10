from faststream import FastStream
from faststream.kafka import KafkaBroker

from ...config.broker import BrokerSettings


def create_kafka_broker(settings: BrokerSettings) -> KafkaBroker:
    """
    Creates and configures a Kafka broker instance.

    Args:
        settings: Broker configuration settings.

    Returns:
        Configured KafkaBroker instance.
    """
    return KafkaBroker(settings.bootstrap_servers)


def create_faststream_app(broker: KafkaBroker) -> FastStream:
    """
    Creates a FastStream application with the given broker.

    Args:
        broker: The Kafka broker instance.

    Returns:
        FastStream application instance.
    """
    return FastStream(broker)


# Default broker and app instances (can be overridden)
_settings = BrokerSettings()
_broker = create_kafka_broker(_settings)
app = create_faststream_app(_broker)

