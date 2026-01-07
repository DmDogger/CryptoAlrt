import uuid
from decimal import Decimal

import structlog

from application.interfaces.event_publisher import EventPublisherProtocol
from application.interfaces.repositories import CryptocurrencyRepositoryProtocol
from config.broker import broker_settings
from domain.exceptions import PublishError, CryptocurrencyNotFound
from domain.services.update_price import PriceUpdateDomainService

logger = structlog.getLogger(__name__)


class PublishPriceUpdateToBrokerUseCase:
    """Use case for publishing cryptocurrency price updates to message broker."""

    def __init__(
        self,
        broker: EventPublisherProtocol,
        repository: CryptocurrencyRepositoryProtocol,
    ):
        """Initialize the use case with required dependencies.

        Args:
            broker: Event publisher for sending messages to broker.
            repository: Repository for accessing cryptocurrency entities.
        """
        self._broker = broker
        self._repository = repository

    async def execute(
        self,
        cryptocurrency_id: uuid.UUID,
        new_price: Decimal,
    ) -> None:
        """Execute price update publishing workflow.

        Retrieves cryptocurrency entity, creates price update event,
        and publishes it to the message broker.

        Args:
            cryptocurrency_id: UUID of the cryptocurrency to update.
            new_price: New price value to publish.

        Raises:
            CryptocurrencyNotFound: If cryptocurrency doesn't exist.
            PublishError: If publishing to broker fails.
        """
        try:
            cryptocurrency = await self._repository.get_by_cryptocurrency_id(
                cryptocurrency_id
            )
            if not cryptocurrency:
                logger.error(
                    f"Occurred error during retrieving cryptocurrency from database"
                )
                raise CryptocurrencyNotFound(f"Cryptocurrency with this ID not found")

            event = await PriceUpdateDomainService.create_price_updated_event(
                cryptocurrency_id=cryptocurrency.id,
                cryptocurrency_symbol=cryptocurrency.symbol,
                cryptocurrency_name=cryptocurrency.name,
                new_price=new_price,
            )
            logger.info(f"Event was created successfully. Event ID: {event.id}")
            await self._broker.publish(
                topic=broker_settings.price_updates_topic,
                event=event.to_dict(),  # ← Конвертируем в dict для JSON сериализации
            )
            logger.info(
                f"Event was successfully published into topic {broker_settings.price_updates_topic}, Event ID: {event.id}"
            )

        except Exception as e:
            logger.error(f"Occurred error during publishing event, error: {e}")
            raise PublishError("Occurred error during publishing event.")
