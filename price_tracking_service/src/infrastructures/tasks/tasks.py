from taskiq import AsyncBroker
from taskiq_redis import RedisAsyncResultBackend, ListQueueBroker
from faststream.kafka import KafkaBroker
import structlog

from application.use_cases.process_price_update import ProcessPriceUpdateUseCase
from config.broker import broker_settings
from config.redis import RedisSettings
from config.scheduler import scheduler_settings
from domain.exceptions import UnexpectedError
from dishka import FromDishka
from dishka.integrations.taskiq import inject, setup_dishka
from infrastructures.di_container import create_container

logger = structlog.getLogger(__name__)

# Настройки Redis
redis_settings = RedisSettings()

# Kafka broker для FastStream (обработка событий)
kafka_broker = KafkaBroker(broker_settings.bootstrap_servers)

# TaskIQ broker для периодических задач (с поддержкой расписания через Redis)
taskiq_broker = ListQueueBroker(
    url=str(redis_settings.redis_url),
    queue_name="taskiq:crypto_alert:queue",  # Уникальное имя очереди
).with_result_backend(
    RedisAsyncResultBackend(
        redis_url=str(redis_settings.redis_url),
        result_ex_time=3600,  # TTL результатов: 1 час
    )
)

# Настраиваем Dishka для TaskIQ worker
container = create_container()
setup_dishka(container, taskiq_broker)


async def startup_kafka_broker():
    """Запускаем Kafka broker для публикации событий."""
    await kafka_broker.start()


async def shutdown_kafka_broker():
    """Останавливаем Kafka broker."""
    await kafka_broker.close()


@taskiq_broker.task(
    task_name="fetch_all_cryptocurrency_prices",
    schedule=[{"cron": scheduler_settings.fetch_interval_cron}],
)
@inject
async def fetch_all_prices_task(
    use_case: FromDishka[ProcessPriceUpdateUseCase],
) -> None:
    """Fetch and save cryptocurrency prices for all configured coins.

    This task runs on schedule and fetches current prices from CoinGecko API
    for all cryptocurrencies specified in configuration, then saves them to database.

    Args:
        use_case: ProcessPriceUpdateUseCase injected by Dishka container.

    Raises:
        Logs UnexpectedError but continues processing remaining coins.

    Example:
        Configured coins: ["bitcoin", "ethereum", "cardano"]
        Each coin is fetched and saved independently.
    """
    await startup_kafka_broker()

    logger.info("[Task]: Starting scheduled price fetch")

    coin_symbols = scheduler_settings.cryptocurrencies

    for symbol in coin_symbols:
        try:
            logger.info(
                f"[TaskIQ]: Trying to fetch and save this coin (symbol): {symbol} information"
            )
            await use_case.execute(coin_id=symbol)
            logger.info(
                f"[TaskIQ]: Successfully fetched and saved information for {symbol} in database"
            )

        except UnexpectedError as e:
            logger.error(f"[Unexpected error]: Unexpected error during fetching from TaskIQ {e}")

    logger.info(f"[Task]: All fetching successfully done.")

    await shutdown_kafka_broker()


from taskiq.scheduler.scheduler import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource

scheduler = TaskiqScheduler(broker=taskiq_broker, sources=[LabelScheduleSource(taskiq_broker)])
