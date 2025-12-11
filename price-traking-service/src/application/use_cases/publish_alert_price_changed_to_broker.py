from decimal import Decimal
from uuid import UUID

import structlog

from application.interfaces.event_publisher import EventPublisherProtocol
from application.interfaces.repositories import CryptocurrencyRepositoryProtocol
from config.broker import broker_settings
from domain.exceptions import CryptocurrencyNotFound, PublishError
from domain.services.create_alert_on_price_change import CreateAlertOnPriceChangeService

logger = structlog.getLogger(__name__)

class PublishAlertPriceChangedToBrokerUseCase:
    """Use case for publishing price change alerts to the message broker.

    Retrieves cryptocurrency data, checks for alerts, and publishes events.
    """
    def __init__(
        self,
        broker: EventPublisherProtocol,
        alert_service: CreateAlertOnPriceChangeService,
        repository: CryptocurrencyRepositoryProtocol
    ):
        self._broker = broker
        self._alert_service = alert_service
        self._repository = repository

    async def execute(
            self,
            cryptocurrency_id: UUID,
            user_email: str,
            new_price: Decimal,
            threshold_percent: Decimal,
            threshold_price: Decimal
    ):
        """Executes the use case to check for price change alerts and publish to broker.

        Args:
            cryptocurrency_id: The ID of the cryptocurrency.
            user_email: The user's email.
            new_price: The new price.
            threshold_percent: The threshold percentage.
            threshold_price: The threshold price.
        """
        try:
            cryptocurrency = await self._repository.get_by_cryptocurrency_id(cryptocurrency_id)

            if cryptocurrency is None:
                logger.error(f"[Not found]: Cryptocurrency with ID {cryptocurrency_id} not exist")
                raise CryptocurrencyNotFound(f"Cryptocurrency with ID {cryptocurrency_id} not found")

            if old_price := await self._repository.get_last_price(cryptocurrency.id):
                alert_event = self._alert_service.create_alert_on_price_change(
                    cryptocurrency_id=cryptocurrency_id,
                    user_email=user_email,
                    old_price=old_price,
                    new_price=new_price,
                    threshold_price=threshold_price,
                    threshold_percent=threshold_percent
                )

                await self._broker.publish(
                    topic=broker_settings.alert_created_topic,
                    event=alert_event
                )
                logger.info(f"[Broker]: Successfully sent message into broker.")
            else:
                logger.error(f"[Not found]: Old price fot this cryptocurrency not found.")

        except Exception as e:
            logger.exception("[Unexpected]: Unexpected error during alert publishing", exc_info=e)
            raise PublishError("Occurred error during publishing event.")



