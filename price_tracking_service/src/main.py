import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from faststream import FastStream
from dishka.integrations.fastapi import setup_dishka as setup_dishka_fastapi
from dishka.integrations.faststream import setup_dishka as setup_dishka_faststream
import structlog

from config.cors import CORSSettings
from infrastructures.di_container import create_container
from infrastructures.tasks.tasks import kafka_broker, taskiq_broker
from presentation.api.v1.controllers.alert import router as alert_router
from presentation.api.v1.controllers.cryptocurrency import (
    router as cryptocurrency_router,
)

logger = structlog.getLogger(__name__)

container = create_container()
cors_settings = CORSSettings()

faststream_app = FastStream(kafka_broker)
setup_dishka_faststream(container, faststream_app)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastStream broker...")
    faststream_task = asyncio.create_task(faststream_app.run())
    logger.info("FastStream broker started")

    logger.info("Starting TaskIQ broker...")
    await taskiq_broker.startup()
    logger.info("TaskIQ broker started")

    yield

    logger.info("Stopping FastStream broker...")
    faststream_task.cancel()
    try:
        await faststream_task
    except asyncio.CancelledError:
        pass
    logger.info("FastStream broker stopped")

    logger.info("Stopping TaskIQ scheduler...")
    await taskiq_broker.shutdown()
    logger.info("TaskIQ scheduler stopped")


fastapi_app = FastAPI(
    title="CryptoAlert by DmDogger",
    description="service.__name__",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_settings.cors_origins,
    allow_credentials=cors_settings.cors_allow_credentials,
    allow_methods=cors_settings.cors_allow_methods,
    allow_headers=cors_settings.cors_allow_headers,
)

setup_dishka_fastapi(container, fastapi_app)

fastapi_app.include_router(alert_router)
fastapi_app.include_router(cryptocurrency_router)


__all__ = ["fastapi_app", "faststream_app"]

app = fastapi_app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:fastapi_app", host="0.0.0.0", port=8002, reload=True, log_level="info")
