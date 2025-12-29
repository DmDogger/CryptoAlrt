"""Broker providers for Dishka dependency injection."""

from dishka import Provider, Scope, provide
from faststream.kafka import KafkaBroker

from src.application.interfaces.event_publisher import EventPublisherProtocol
from src.config.broker import BrokerSettings
from src.infrastructures.broker.publisher import KafkaEventPublisher


class BrokerProvider(Provider):
    """Provider for message broker-related dependencies."""

    @provide(scope=Scope.APP)
    def provide_broker_settings(self) -> BrokerSettings:
        """Provide BrokerSettings instance."""
        return BrokerSettings()

    @provide(scope=Scope.APP)
    def provide_kafka_broker(
        self,
        settings: BrokerSettings,
    ) -> KafkaBroker:
        """Provide KafkaBroker instance."""
        return KafkaBroker(settings.bootstrap_servers)

    @provide(scope=Scope.APP)
    def provide_event_publisher(
        self,
        broker: KafkaBroker,
    ) -> EventPublisherProtocol:
        """Provide KafkaEventPublisher instance."""
        return KafkaEventPublisher(broker=broker)
