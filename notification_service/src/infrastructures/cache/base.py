from typing import Any

from config.cache import cache_settings


class BaseCache:
    prefix = "c"

    def __init__(self, version=None, prefix=None):
        self.version = version or cache_settings.CACHE_VERSION
        if prefix is not None:
            self.prefix = prefix

    @staticmethod
    def _wrap_key(prefix: str, version: Any, key: Any) -> str:
        return f"{prefix}:{version}:{key}"

    @staticmethod
    def unwrap_key(prefix: str, version: Any, value: str) -> str:
        header = f"{prefix}:{version}"
        if value[: len(header)] != header:
            raise ValueError("invalid key header")
        return value[len(header) + 1 :]

    def make_key(self, key, version=None) -> str:
        return self._wrap_key(self.prefix, version or self.version, key)

    def set(self, key: Any, value: Any, timeout: int, version=None):
        raise NotImplementedError

    def delete(self, key: Any, version=None):
        raise NotImplementedError

    def get(self, key: Any, version=None):
        raise NotImplementedError
