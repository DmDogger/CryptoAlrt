from abc import abstractmethod
from typing import Any, Protocol


class EventPublisherProtocol(Protocol):
    """
    Protocol for event publishing.

    Defines methods for publishing domain events to external systems (e.g., Kafka).
    This interface allows the Application layer to publish events without
    depending on Infrastructure implementations.
    """

    @abstractmethod
    async def publish(self, topic: str, event: Any) -> None:
        """
        Publishes an event to the specified topic.

        Args:
            topic: The Kafka topic name to publish to.
            event: The event object to publish (DTO, entity, etc.).
                FastStream will automatically serialize it.

        Raises:
            PublishError: If publishing fails.
        """
        ...
