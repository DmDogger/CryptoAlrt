from decimal import Decimal

import structlog

from application.interfaces.event_publisher import EventPublisherProtocol
from application.interfaces.repositories import AlertRepositoryProtocol
from config.broker import broker_settings
from domain.events.threshold_triggered import ThresholdTriggeredEvent
from domain.exceptions import PublishError, RepositoryError
from domain.services.check_threshold import CheckThresholdService

logger = structlog.getLogger(__name__)


class CheckThresholdUseCase:
    """Use case for checking alert thresholds and publishing triggered events.
    
    This use case retrieves all active alerts for a cryptocurrency,
    checks if the current price meets any threshold conditions,
    and publishes threshold triggered events for matching alerts.
    """
    
    def __init__(
            self,
            alert_repository: AlertRepositoryProtocol,
            event_publisher: EventPublisherProtocol,
    ):
        """Initialize the use case with required dependencies.
        
        Args:
            alert_repository: Repository for accessing alert entities.
            event_publisher: Publisher for sending events to message broker.
        """
        self._alert_repository = alert_repository
        self._event_publisher = event_publisher

    async def execute(
            self,
            cryptocurrency: str,
            current_price: Decimal
    ) -> None:
        """Execute threshold checking and event publishing workflow.
        
        Retrieves all active alerts for the specified cryptocurrency,
        checks each alert's threshold against the current price,
        and publishes events for alerts that have been triggered.
        
        Args:
            cryptocurrency: Name of the cryptocurrency (e.g., Bitcoin, Ethereum).
            current_price: Current price of the cryptocurrency to check against thresholds.
            
        Raises:
            RepositoryError: If database error occurs during alert retrieval.
            PublishError: If publishing event to broker fails.
        """
        try:
            logger.info(
                "Starting threshold check for cryptocurrency",
                cryptocurrency=cryptocurrency,
                current_price=str(current_price)
            )
            
            alerts = await self._alert_repository.get_active_alerts_by_name(crypto_name=cryptocurrency)
            
            if not alerts:
                logger.info(
                    "No active alerts found for cryptocurrency",
                    cryptocurrency=cryptocurrency
                )
                return
            
            logger.info(
                f"Checking {len(alerts)} active alert(s)",
                cryptocurrency=cryptocurrency,
                alerts_count=len(alerts)
            )
            
            triggered_count = 0
            for alert in alerts:
                if CheckThresholdService.check_threshold(
                    alert_entity=alert,
                    price_to_check=current_price
                ):
                    logger.info(
                        "Alert threshold triggered",
                        alert_id=str(alert.id),
                        cryptocurrency=cryptocurrency,
                        threshold_price=str(alert.threshold_price.value),
                        current_price=str(current_price),
                        email=alert.email
                    )
                    
                    trigger_event = ThresholdTriggeredEvent.create(
                        alert_id=alert.id,
                        current_price=current_price,
                        cryptocurrency=cryptocurrency,
                        threshold_price=alert.threshold_price.value
                    )
                    
                    await self._event_publisher.publish(
                        topic=broker_settings.alert_triggered_topic,
                        event=trigger_event
                    )
                    
                    triggered_count += 1
                    
                    logger.info(
                        "Threshold triggered event published",
                        event_id=str(trigger_event.id),
                        alert_id=str(alert.id),
                        topic=broker_settings.alert_triggered_topic
                    )
            
            logger.info(
                "Threshold check completed",
                cryptocurrency=cryptocurrency,
                total_alerts=len(alerts),
                triggered_alerts=triggered_count
            )
            
        except RepositoryError as e:
            logger.error(
                "Repository error during threshold check",
                cryptocurrency=cryptocurrency,
                error=str(e)
            )
            raise
            
        except PublishError as e:
            logger.error(
                "Failed to publish threshold triggered event",
                cryptocurrency=cryptocurrency,
                error=str(e)
            )
            raise
            
        except Exception as e:
            logger.error(
                "Unexpected error during threshold check",
                cryptocurrency=cryptocurrency,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )
            raise
