"""
CachedRepository pattern
Original idea: https://ardalis.com/building-a-cachedrepository-in-aspnet-core/
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from json import JSONDecodeError
from typing import final
from uuid import UUID

import redis
import structlog

from application.interfaces.repositories import PreferenceRepositoryProtocol
from config.cache import cache_settings
from domain.entities.user_preference import UserPreferenceEntity
from infrastructures.cache.redis import RedisCache
from infrastructures.database.mappers import UserPreferenceDBMapper
from infrastructures.database.repositories import SQLAlchemyUserPreferenceRepository

logger = structlog.getLogger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CachedUserPreferencyRepository(PreferenceRepositoryProtocol):
    # todo: add all protocols methods
    _original: SQLAlchemyUserPreferenceRepository
    _redis_cache: RedisCache
    _mapper: UserPreferenceDBMapper

    async def get_by_id(self, preference_id: UUID) -> UserPreferenceEntity | None:
        """
        Searches for user preferences in the cache (by pref.id), if found, it returns them;
        if not, it makes a request to the original repository, saves them in the cache,
        and returns the result
        """
        try:
            logger.debug(
                "Starting to get preferences by id from cache", preference_id=preference_id
            )
            preferences: dict | None = await self._redis_cache.get(key=preference_id)

            if not preferences:
                logger.debug(
                    "Preferences in cache not found, I will try ask repository",
                    preference_id=preference_id,
                )
                result = await self._original.get_by_id(preference_id=preference_id)

                if result is None:
                    return None

                await self._redis_cache.set(
                    key=preference_id,
                    value=self._mapper.to_dict(result),
                    timeout=cache_settings.key_expire,
                )
                logger.debug(
                    "Preferences saved to cache successfully",
                    key=preference_id,
                    value=result,
                    ttl=cache_settings.key_expire,
                )
                return result

            return UserPreferenceEntity.from_dict(preferences)

        except (redis.exceptions.DataError, JSONDecodeError) as e:
            # Data errors occur when there are problems with the data itself,
            # Such as serialization failures, or data corruption. (source: redis.io)
            logger.error(
                "Redis operation failed",
                error_type=type(e).__name__,
                operation="get",
                key=preference_id,
                timestamp=datetime.now(UTC).isoformat(),
            )
            await self._redis_cache.delete(
                key=preference_id,
            )
            return await self._original.get_by_id(preference_id)

        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            # Connection errors are usually temporary,
            # so implementing retry logic or fallback strategies is recommended.
            # TODO: add retry logic
            logger.error(
                "Redis operation failed",
                error_type=type(e).__name__,
                operation="get",
                key=preference_id,
                timestamp=datetime.now(UTC).isoformat(),
            )
            return await self._original.get_by_id(preference_id)

    async def get_by_email(self, email: str) -> UserPreferenceEntity | None:
        """Searches for user preferences (by email) in the cache, if found, it returns them;
        if not, it makes a request to the original repository, saves them in the cache,
        and returns the result"""
        try:
            preferences: dict | None = await self._redis_cache.get(key=email)

            if not preferences:
                result = await self._original.get_by_email(email)

                if result is None:
                    return None

                await self._redis_cache.set(
                    key=email,
                    value=self._mapper.to_dict(result),
                    timeout=cache_settings.key_expire,
                )
                return result
            return UserPreferenceEntity.from_dict(preferences)
        except (redis.exceptions.DataError, JSONDecodeError) as e:
            logger.error(
                "Redis operation failed",
                error_type=type(e).__name__,
                operation="get",
                key=email,
                timestamp=datetime.now(UTC).isoformat(),
            )
            await self._redis_cache.delete(key=email)
            return await self._original.get_by_email(email)
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            logger.error(
                "Redis operation failed",
                error_type=type(e).__name__,
                operation="get",
                key=email,
                timestamp=datetime.now(UTC).isoformat(),
            )
            return await self._original.get_by_email(email=email)

    async def get_by_telegram_id(self, telegram_id: int) -> UserPreferenceEntity | None:
        # todo: will be realised
        pass

    async def save(self, preference: UserPreferenceEntity) -> UserPreferenceEntity:
        pass

    async def update(self, preference: UserPreferenceEntity) -> UserPreferenceEntity:
        pass
