from dataclasses import dataclass
from datetime import datetime, UTC
from decimal import Decimal
from json import JSONDecodeError
from typing import final, Any

import redis
import structlog

from application.interfaces import PortfolioRepositoryProtocol
from infrastructures.database.mappers.portfolio_db_mapper import PortfolioDBMapper

from domain.entities.portfolio_entity import PortfolioEntity

from config.cache import cache_settings
from infrastructures.cache.redis import RedisCache

logger = structlog.getLogger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CachedPortfolioRepository:  # todo: implement all protocol's methods
    _redis_client: RedisCache
    _original: PortfolioRepositoryProtocol
    _mapper: PortfolioDBMapper

    async def get_portfolio_with_assets_and_prices(
        self, wallet_address: str
    ) -> PortfolioEntity | None:
        """
        The method searches the cache for a saved portfolio entity with assets.
        If it does not find one, it queries the database and saves the value to the cache.
        """
        try:
            logger.debug(
                "Starting to get portfolio with assets and prices by wallet from cache",
                wallet_address=wallet_address,
            )
            portfolio: dict | None = await self._redis_client.get(
                key=wallet_address, version=cache_settings.version_with_assets_and_prices
            )

            if portfolio is None:
                logger.debug(
                    "Nothing found in cache, I will ask repository",
                    wallet_address=wallet_address,
                )

                result = await self._original.get_portfolio_with_assets_and_prices(
                    wallet_address=wallet_address
                )

                if result is None:
                    logger.debug("Nothing found in database")
                    return None

                cache_dict = self._mapper.to_dict(result)
                if isinstance(cache_dict.get("updated_at"), datetime):
                    cache_dict["updated_at"] = cache_dict["updated_at"].isoformat()

                await self._redis_client.set(
                    key=wallet_address,
                    version=cache_settings.version_with_assets_and_prices,
                    value=cache_dict,
                    timeout=cache_settings.key_expire,
                )

                logger.debug("Successfully found in database and cached")
                return result
            return self._mapper.from_dict(portfolio)

        except (redis.exceptions.DataError, JSONDecodeError) as e:
            logger.error(
                "Redis operation failed",
                error_type=type(e).__name__,
                operation="get",
                key=wallet_address,
                timestamp=datetime.now(UTC).isoformat(),
            )
            await self._redis_client.delete(
                key=wallet_address,
                version=cache_settings.version_with_assets_and_prices,
            )
            return await self._original.get_portfolio_with_assets_and_prices(
                wallet_address=wallet_address
            )

        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            logger.error(
                "Redis operation failed",
                error_type=type(e).__name__,
                operation="get",
                key=wallet_address,
                version=cache_settings.version_with_assets_and_prices,
                timestamp=datetime.now(UTC).isoformat(),
            )
            return await self._original.get_portfolio_with_assets_and_prices(
                wallet_address=wallet_address
            )

    async def get_portfolio_total_value(
        self, wallet_address: str
    ) -> tuple[PortfolioEntity, Decimal] | None:
        try:
            portfolio: dict | None = await self._redis_client.get(
                key=wallet_address, version=cache_settings.version_with_assets_and_prices
            )
            total_value: dict | None = await self._redis_client.get(
                key=wallet_address, version=cache_settings.version_total_value
            )

            if not portfolio or not total_value:
                portfolio_entity, total_value_decimal = (
                    await self._original.get_portfolio_total_value(wallet_address=wallet_address)
                )

                if portfolio_entity is None or total_value_decimal is None:
                    return None

                cache_dict = self._mapper.to_dict(portfolio_entity)
                if isinstance(cache_dict.get("updated_at"), datetime):
                    cache_dict["updated_at"] = cache_dict["updated_at"].isoformat()

                await self._redis_client.set(
                    key=wallet_address,
                    version=cache_settings.version_portfolio_total_value,
                    value=cache_dict,
                    timeout=cache_settings.key_expire,
                )

                await self._redis_client.set(
                    key=wallet_address,
                    version=cache_settings.version_total_value,
                    value=str(total_value_decimal),
                    timeout=cache_settings.key_expire,
                )
                return portfolio_entity, total_value_decimal
            return self._mapper.from_dict(portfolio), self._mapper.to_decimal(total_value)

        except (redis.exceptions.DataError, JSONDecodeError) as e:
            logger.error(
                "Redis operation failed",
                error_type=type(e).__name__,
                operation="get",
                key=wallet_address,
                timestamp=datetime.now(UTC).isoformat(),
            )
            await self._redis_client.delete(
                key=wallet_address,
                version=cache_settings.version_total_value,
            )
            await self._redis_client.delete(
                key=wallet_address,
                version=cache_settings.version_portfolio_total_value,
            )

            return await self._original.get_portfolio_total_value(wallet_address=wallet_address)

        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            logger.error(
                "Redis operation failed",
                error_type=type(e).__name__,
                operation="get",
                key=wallet_address,
                version=cache_settings.version_with_assets_and_prices,
                timestamp=datetime.now(UTC).isoformat(),
            )
            return await self._original.get_portfolio_total_value(wallet_address=wallet_address)

    async def get_portfolio_with_assets_count(
        self, wallet_address: str
    ) -> tuple[PortfolioEntity, int] | None:
        try:
            logger.debug(
                "Trying to get portfolio with assets counted from cache",
                wallet_address=wallet_address,
            )
            assets_counted: int | None = await self._redis_client.get(
                key=wallet_address,
                version=cache_settings.assets_counted,
            )
            portfolio: Any | None = await self._redis_client.get(
                key=wallet_address,
                version=cache_settings.portfolio_assotiated_with_assets_counted,
            )

            if not assets_counted or not portfolio:
                # if nothing found, let repository find the values
                logger.debug(
                    "Nothing found, I will ask repository",
                    wallet_address=wallet_address,
                )
                portfolio, assets_counted = await self._original.get_portfolio_with_assets_count(
                    wallet_address=wallet_address
                )

                if portfolio is None or assets_counted is None:
                    logger.debug("Nothing found in database")
                    return None

                cache_dict = self._mapper.to_dict(portfolio)
                if isinstance(cache_dict.get("updated_at"), datetime):
                    cache_dict["updated_at"] = cache_dict["updated_at"].isoformat()

                await self._redis_client.set(
                    key=wallet_address,
                    value=cache_dict,
                    version=cache_settings.portfolio_assotiated_with_assets_counted,
                    timeout=cache_settings.key_expire,
                )

                await self._redis_client.set(
                    key=wallet_address,
                    value=assets_counted,
                    version=cache_settings.assets_counted,
                    timeout=cache_settings.key_expire,
                )
                logger.debug("Successfully found in database and cached")
                # no need to convert because data from repository layer already converted
                return portfolio, assets_counted
            return self._mapper.from_dict(portfolio), assets_counted
        except (redis.exceptions.DataError, JSONDecodeError) as e:
            logger.error(
                "Redis operation failed",
                error_type=type(e).__name__,
                operation="get",
                key=wallet_address,
                timestamp=datetime.now(UTC).isoformat(),
            )
            await self._redis_client.delete(
                key=wallet_address,
                version=cache_settings.portfolio_assotiated_with_assets_counted,
            )
            await self._redis_client.delete(
                key=wallet_address,
                version=cache_settings.assets_counted,
            )
            return await self._original.get_portfolio_with_assets_count(
                wallet_address=wallet_address
            )
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            logger.error(
                "Redis operation failed",
                error_type=type(e).__name__,
                operation="get",
                key=wallet_address,
                version=cache_settings.portfolio_assotiated_with_assets_counted,
                timestamp=datetime.now(UTC).isoformat(),
            )
            return await self._original.get_portfolio_with_assets_count(
                wallet_address=wallet_address
            )
