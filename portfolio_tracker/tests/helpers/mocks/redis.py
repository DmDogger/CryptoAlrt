from typing import AsyncGenerator, Any

import pytest_asyncio
from testcontainers.redis import AsyncRedisContainer


@pytest_asyncio.fixture
async def mock_redis_client() -> AsyncGenerator[Any, Any]:
    """RedisClient через TestConatiner"""
    with AsyncRedisContainer() as redis_container:
        redis_client = await redis_container.get_async_client()
        yield redis_client
        await redis_client.aclose()
