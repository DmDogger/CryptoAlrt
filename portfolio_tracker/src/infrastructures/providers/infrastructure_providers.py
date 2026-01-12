from typing import AsyncIterable

import redis
from dishka import Provider, provide, Scope
from redis import Redis

from infrastructures.redis.redis import r as r_client


class InfrastructureProviders(Provider):
    @provide(scope=Scope.APP)
    async def get_redis_client(self) -> AsyncIterable[Redis]:
        try:
            await r_client.ping()
            yield r_client
        except redis.exceptions.ConnectionError:
            await r_client.aclose()
