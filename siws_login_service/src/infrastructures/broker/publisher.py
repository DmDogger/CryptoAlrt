from dataclasses import dataclass
from typing import Any, final

from faststream.kafka import KafkaBroker
from structlog import getLogger

from application.interfaces.event_publisher import EventPublisherProtocol
from infrastructures.exceptions import PublicationError

logger = getLogger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class KafkaEventPublisher(EventPublisherProtocol):
    """
    Kafka implementation of EventPublisherProtocol.

    Publishes events to Kafka using FastStream broker.
    FastStream automatically serializes any object to JSON.
    """

    broker: KafkaBroker

    async def publish(self, topic: str, event: Any) -> None:
        """
        Publishes an event to the specified Kafka topic.

        Args:
            topic: The Kafka topic name to publish to.
            event: The event object to publish (DTO, entity, etc.).
                FastStream will automatically serialize it to JSON.

        Raises:
            PublishError: If publishing fails.
        """
        try:
            await self.broker.publish(
                message=event,
                topic=topic
            )

            logger.info(
                "Event published successfully",
                topic=topic,
                event_type=type(event).__name__
            )
        except Exception as e:
            logger.error(
                "Failed to publish event",
                error=str(e),
                topic=topic,
                event_type=type(event).__name__,
                exc_info=True
            )
            raise PublicationError(
                f"Failed to publish event to topic '{topic}': {e}"
            ) from e





