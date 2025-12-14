"""
Приложение сочетает FastAPI (HTTP API) и FastStream (асинхронная обработка сообщений).

Запуск:
- python main.py                    # FastAPI + FastStream (основной режим)
- python main.py --faststream-only  # Только FastStream (для разработки)
- fastapi run main.py              # Через FastAPI CLI
- uvicorn main:fastapi_app         # Через uvicorn напрямую
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from faststream import FastStream
from dishka.integrations.fastapi import setup_dishka as setup_dishka_fastapi
from dishka.integrations.faststream import setup_dishka as setup_dishka_faststream
import structlog

from infrastructures.di_container import create_container
from infrastructures.tasks.tasks import kafka_broker
from presentation.api.v1.controllers.alert import router as alert_router

logger = structlog.getLogger(__name__)

container = create_container()

faststream_app = FastStream(kafka_broker)
setup_dishka_faststream(container, faststream_app)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastStream broker...")
    faststream_task = asyncio.create_task(faststream_app.run())
    logger.info("FastStream broker started")


    logger.info("Task registration skipped - run workers separately")

    yield

    logger.info("Stopping FastStream broker...")
    faststream_task.cancel()
    try:
        await faststream_task
    except asyncio.CancelledError:
        pass
    logger.info("FastStream broker stopped")


fastapi_app = FastAPI(
    title="CryptoAlert by DmDogger",
    description="service.__name__",
    version="1.0.0",
    lifespan=lifespan
)

setup_dishka_fastapi(container, fastapi_app)

fastapi_app.include_router(alert_router)


__all__ = ["fastapi_app", "faststream_app"]

app = fastapi_app


if __name__ == "__main__":
    import uvicorn
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--faststream-only":
        logger.info("Running FastStream only...")
        asyncio.run(faststream_app.run())
    else:
        logger.info("Running FastAPI with FastStream...")
        uvicorn.run(
            "main:fastapi_app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )




