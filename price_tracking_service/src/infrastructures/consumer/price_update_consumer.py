from decimal import Decimal

import structlog
from dishka import FromDishka

from application.use_cases.check_threshold import CheckThresholdUseCase
from config.broker import broker_settings
from domain.events.price_updated import PriceUpdatedEvent
from domain.exceptions import RepositoryError, PublishError
from infrastructures.broker.broker import broker

logger = structlog.getLogger(__name__)


async def _consume_price_update_and_check_thresholds(
        event: PriceUpdatedEvent,
        use_case: CheckThresholdUseCase
) -> None:
    """
    Consumer for price update events from the message broker.
    
    This function consumes price update messages from the configured topic and 
    triggers the threshold checking use case to determine if any user-defined 
    price alerts should be triggered based on the new cryptocurrency price.
    
    Args:
        event: event
        use_case (FromDishka[CheckThresholdUseCase]): The injected use case for checking thresholds.
    
    Returns:
        None
    
    Raises:
        Exception: Logs all exceptions but does not re-raise to prevent message reprocessing failures.
    
    Note:
        This consumer is registered to listen to the topic defined in broker_settings.price_updates_topic.
        All errors are caught and logged to ensure the consumer remains stable.
    """
    logger.info(
        "[Consumer] Received price update message",
        cryptocurrency=event.cryptocurrency,
        current_price=str(event.price),
        topic=broker_settings.price_updates_topic
    )
    
    try:
        logger.debug(
            "[Consumer] Starting threshold check use case execution",
            cryptocurrency=event.cryptocurrency,
            current_price=str(event.price)
        )
        
        await use_case.execute(
            cryptocurrency=event.cryptocurrency,
            current_price=event.price
        )
        
        logger.info(
            "[Consumer] Successfully processed price update and checked thresholds",
            cryptocurrency=event.cryptocurrency,
            current_price=str(event.price)
        )
        
    except RepositoryError as e:
        logger.error(
            "[Consumer] Database repository error occurred while processing price update",
            error=str(e),
            error_type=type(e).__name__,
            cryptocurrency=event.cryptocurrency,
            current_price=str(event.price),
            topic=broker_settings.price_updates_topic,
            exc_info=True
        )
        
    except PublishError as e:
        logger.error(
            "[Consumer] Message publishing error occurred while processing price update",
            error=str(e),
            error_type=type(e).__name__,
            cryptocurrency=event.cryptocurrency,
            current_price=str(event.price),
            topic=broker_settings.price_updates_topic,
            exc_info=True
        )
        
    except ValueError as e:
        logger.error(
            "[Consumer] Invalid data format received in price update message",
            error=str(e),
            error_type=type(e).__name__,
            cryptocurrency=event.cryptocurrency,
            current_price=str(event.price),
            topic=broker_settings.price_updates_topic,
            exc_info=True
        )
        
    except Exception as e:
        logger.critical(
            "[Consumer] Unexpected error occurred while processing price update",
            error=str(e),
            error_type=type(e).__name__,
            cryptocurrency=event.cryptocurrency,
            current_price=str(event.price),
            topic=broker_settings.price_updates_topic,
            exc_info=True
        )


@broker.subscriber(
    title="consume_price_update_and_check_threshold",
    topic=broker_settings.price_updates_topic
)
async def consume_price_update_and_check_thresholds(
        event: PriceUpdatedEvent,
        use_case: FromDishka[CheckThresholdUseCase]
) -> None:
    """
    Consumer for price update events from the message broker.

    This function consumes price update messages from the configured topic and
    triggers the threshold checking use case to determine if any user-defined
    price alerts should be triggered based on the new cryptocurrency price.

    Args:
        event: Price update event
        use_case (FromDishka[CheckThresholdUseCase]): The injected use case for checking thresholds.

    Returns:
        None

    Raises:
        Exception: Logs all exceptions but does not re-raise to prevent message reprocessing failures.

    Note:
        This consumer is registered to listen to the topic defined in broker_settings.price_updates_topic.
        All errors are caught and logged to ensure the consumer remains stable.
    """
    await _consume_price_update_and_check_thresholds(event, use_case)

