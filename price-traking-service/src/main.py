from faststream import FastStream
from dishka.integrations.faststream import setup_dishka
import structlog

from infrastructures.di_container import create_container
from infrastructures.tasks.tasks import kafka_broker, taskiq_broker, register_tasks

logger = structlog.getLogger(__name__)

# Создаём Dishka контейнер
container = create_container()

# FastStream приложение
app = FastStream(kafka_broker)

# Интегрируем Dishka с FastStream
setup_dishka(container, app)

# Регистрируем задачи
register_tasks(taskiq_broker)


@app.on_startup
async def startup():
    """Инициализация при старте приложения."""
    logger.info("[Startup]: ✅ Application started with Dishka DI")
    logger.info("[Startup]: 📅 Scheduled tasks registered")
    logger.info("[Startup]: 🚀 Price tracking service is running")


@app.on_shutdown
async def shutdown():
    """Очистка ресурсов при остановке."""
    logger.info("[Shutdown]: 🛑 Closing Dishka container")
    await container.close()
    logger.info("[Shutdown]: ✅ Application stopped gracefully")


if __name__ == "__main__":
    import asyncio
    asyncio.run(app.run())