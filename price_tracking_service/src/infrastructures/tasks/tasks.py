from taskiq import AsyncBroker
from taskiq_faststream import BrokerWrapper
from faststream.kafka import KafkaBroker
import structlog

from application.use_cases.process_price_update import ProcessPriceUpdateUseCase
from config.broker import broker_settings
from config.scheduler import scheduler_settings
from domain.exceptions import UnexpectedError

logger = structlog.getLogger(__name__)

kafka_broker = KafkaBroker(broker_settings.bootstrap_servers)
taskiq_broker = BrokerWrapper(kafka_broker)


async def fetch_all_prices_task() -> None:
    """Fetch and save cryptocurrency prices for all configured coins.

    This task runs on schedule and fetches current prices from CoinGecko API
    for all cryptocurrencies specified in configuration, then saves them to database.

    Raises:
        Logs UnexpectedError but continues processing remaining coins.

    Example:
        Configured coins: ["bitcoin", "ethereum", "cardano"]
        Each coin is fetched and saved independently.
    """
    from infrastructures.di_container import create_container

    logger.info("[Task]: Starting scheduled price fetch")

    # Create DI container and get dependencies
    container = create_container()
    coin_symbols = scheduler_settings.cryptocurrencies

    async with container() as request_container:
        use_case = request_container.get(ProcessPriceUpdateUseCase)

        for symbol in coin_symbols:
            try:
                logger.info(f"[TaskIQ]: Trying to fetch and save this coin (symbol): {symbol} information")
                await use_case.execute(coin_id=symbol)
                logger.info(f"[TaskIQ]: Successfully fetched and saved information for {symbol} in database")

            except UnexpectedError as e:
                logger.error(f"[Unexpected error]: Unexpected error during fetching from TaskIQ {e}")

    logger.info(f"[Task]: All fetching successfully done.")


def register_tasks(broker: AsyncBroker) -> None:
    """Register all Taskiq tasks with the broker.
    
    This function registers periodic and on-demand tasks for the price tracking service.
    Tasks are registered with their names and schedules for automatic execution.
    
    Args:
        broker: AsyncBroker instance to register tasks with.
    
    Registered tasks:
        - fetch_all_cryptocurrency_prices: Periodic task that runs on cron schedule
          to fetch and save prices for all configured cryptocurrencies.
    """
    broker.register_task(
        fetch_all_prices_task,
        task_name="fetch_all_cryptocurrency_prices",
        schedule=[{"cron": scheduler_settings.fetch_interval_cron}],
    )





