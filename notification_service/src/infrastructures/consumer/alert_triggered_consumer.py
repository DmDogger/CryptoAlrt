import structlog
from dishka import FromDishka

from application.use_cases.process_alert_triggered_use_case import (
    ProcessAlertTriggeredUseCase,
)
from config.broker import broker_settings
from domain.events.alert_triggered import AlertTriggeredEvent
from infrastructures.broker.broker import broker

logger = structlog.getLogger(__name__)


@broker.subscriber(
    broker_settings.alert_triggered_topic, title="consume_alert_triggered"
)
async def consume_alert_triggered(
    event: AlertTriggeredEvent,
    use_case: FromDishka[ProcessAlertTriggeredUseCase],
) -> None:
    """Consumer for alert triggered events from price_tracking_service.

    This function consumes alert trigger messages from Kafka and
    triggers the notification processing use case.

    Args:
        event: Alert triggered event from Kafka.
        use_case: Injected use case for processing notifications.
    """
    logger.info(
        "Received alert triggered event",
        event_id=event.id,
        email=event.email,
        alert_id=event.alert_id,
        cryptocurrency=event.cryptocurrency,
        current_price=event.current_price,
    )

    await use_case.execute(event)
