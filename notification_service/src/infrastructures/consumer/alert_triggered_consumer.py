from application.use_cases.check_and_reserve import CheckAndReserveUseCase
from dishka import FromDishka

from config.broker import broker_settings
from infrastructures.broker.broker import broker
from ...presentation.v1.schemas.alert_triggered import AlertTriggeredDTO


@broker.subscriber(
    topic=broker_settings.alert_triggered_topic,
    title="alert_triggered"
)
async def consume_alert_triggered(
        event: AlertTriggeredDTO,
        use_case: FromDishka[CheckAndReserveUseCase]
):...
