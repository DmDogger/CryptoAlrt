from contextlib import asynccontextmanager

import structlog
from redis.asyncio import Redis

logger = structlog.getLogger(__name__)


@asynccontextmanager
async def on_startup(redis_client: Redis):
    try:
        yield redis_client
    except Exception as e:
        logger.error(
            "Occurred error on startup",
            error=str(e),
            err_typ=type(e).__name__,
        )
