import json
from typing import Any

from config.cache import cache_settings
from infrastructures.cache.base import BaseCache
from infrastructures.exceptions import ValueTooLarge


class RedisCache(BaseCache):
    def __init__(self, client, **options):
        super().__init__(**options)
        self._client = client

    async def set(self, key: Any, value: Any, timeout: int, version=None, raw=False) -> None:
        key = self.make_key(key, version=version)
        v = json.dumps(value) if not raw else value
        if len(v) > cache_settings.max_size:
            raise ValueTooLarge(f"Cache key too large: {key!r} {len(v)!r}")
        await self._client.set(key, v, ex=timeout)

    async def delete(self, key, version=None) -> None:
        key = self.make_key(key, version=version)
        await self._client.delete(key)

    async def get(self, key, version=None) -> Any | None:
        key = self.make_key(key, version=version)
        result = await self._client.get(key)
        if result is not None:
            result = json.loads(result)
        return result
