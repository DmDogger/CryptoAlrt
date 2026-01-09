"""Repository for portfolio database operations using SQLAlchemy.

This module provides data access layer for portfolio entities with assets and prices.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import final

import structlog
from sqlalchemy import select, label, func, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructures.database.mappers.portfolio_db_mapper import PortfolioDBMapper
from domain.entities.portfolio_entity import PortfolioEntity
from infrastructures.database.models.portfolio import Portfolio
from infrastructures.database.models.cryptoprice import CryptoPrice
from infrastructures.database.models.asset import Asset
from sqlalchemy.orm import joinedload

from domain.exceptions import RepositoryError
from application.interfaces.repositories import PortfolioRepositoryProtocol

logger = structlog.getLogger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class SQLAlchemyPortfolioRepository(PortfolioRepositoryProtocol):
    """Repository for portfolio database operations.

    Handles CRUD operations for portfolios with eager loading of assets and prices.
    Mapping logic is delegated to PortfolioDBMapper.
    """

    _session: AsyncSession
    _mapper: PortfolioDBMapper

    async def get_portfolio_with_assets_and_prices(
        self, wallet_address: str
    ) -> PortfolioEntity | None:
        """Retrieve portfolio with assets and their current prices.

        Args:
            wallet_address: Wallet address to find portfolio.

        Returns:
            PortfolioEntity with loaded assets and prices, or None if not found.

        Raises:
            RepositoryError: If database operation fails.
        """
        try:
            logger.debug(
                "Trying to get portfolio information",
                wallet_address=wallet_address,
            )
            stmt = (
                select(Portfolio)
                .distinct()
                .join(Asset, Asset.wallet_address == Portfolio.wallet_address)
                .join(CryptoPrice, Asset.ticker == CryptoPrice.cryptocurrency)
                .where(Portfolio.wallet_address == wallet_address)
                .options(
                    joinedload(
                        Portfolio.assets,
                    ).joinedload(
                        Asset.crypto_price,
                    )
                )
            )
            res = await self._session.execute(stmt)
            portfolio = res.scalar_one_or_none()

            if portfolio is None:
                logger.warning(
                    "Nothing found",
                    wallet_address=wallet_address,
                )
                return None

            logger.debug(
                "Portfolio with assets successfully found",
                wallet_address=wallet_address,
            )
            return self._mapper.from_database(portfolio)

        except SQLAlchemyError as e:
            logger.error(
                "Error during retrieving from database",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError("Unable to load portfolio information") from e

        except Exception as e:
            logger.error(
                "Unexpected error occurred during from database",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError("Unable to load portfolio information") from e

    async def get_portfolio_total_value(
        self, wallet_address: str
    ) -> tuple[PortfolioEntity, Decimal] | None:
        """Calculate and retrieve portfolio total value.

        Total value is calculated as sum of (asset.amount * crypto_price.price).

        Args:
            wallet_address: Wallet address to find portfolio.

        Returns:
            Tuple of (PortfolioEntity, total_value), or None if not found.

        Raises:
            RepositoryError: If database operation fails.
        """
        try:
            logger.debug("Trying to get portfolio total_value & portfolio entity ")
            stmt = (
                select(Portfolio, func.sum(Asset.amount * CryptoPrice.price).label("total_value"))
                .join(Asset, Asset.wallet_address == Portfolio.wallet_address)
                .join(CryptoPrice, CryptoPrice.cryptocurrency == Asset.ticker)
                .where(Portfolio.wallet_address == wallet_address)
                .group_by(Portfolio.wallet_address)
            )
            res = await self._session.execute(stmt)
            row = res.one_or_none()

            if row is None:
                logger.warning(
                    "Nothing found",
                    wallet_address=wallet_address,
                )
                return None

            portfolio_model, total_value = row

            if total_value is None:
                logger.info(
                    "Total value not calculated because it's none",
                    wallet_address=wallet_address,
                )
                total_value = Decimal("0")

            mapped_portfolio = self._mapper.from_database(portfolio_model)

            logger.debug(
                "Portfolio and total value successfully retrieved",
                wallet_address=wallet_address,
                total_value_typ=type(total_value).__name__,
            )
            return mapped_portfolio, total_value

        except SQLAlchemyError as e:
            logger.error(
                "Error occurred during from database",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError("Portfolio and total value successfully retrieved") from e

        except Exception as e:
            logger.error(
                "Unexpected error occurred during from database",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError(
                "Unable to load or calculate assets & portfolio information"
            ) from e

    async def get_portfolio_with_assets_count(
        self, wallet_address: str
    ) -> tuple[PortfolioEntity, int] | None:
        """Retrieve portfolio with count of associated assets.

        Args:
            wallet_address: Wallet address to find portfolio.

        Returns:
            Tuple of (PortfolioEntity, assets_count), or None if not found.

        Raises:
            RepositoryError: If database operation fails.
        """
        try:
            logger.debug(
                "Trying to get portfolio information & assets count",
                wallet_address=wallet_address,
            )
            stmt = (
                select(Portfolio, func.count(Asset.asset_id).label("total_assets_count"))
                .join(Asset, Asset.wallet_address == Portfolio.wallet_address)
                .where(Portfolio.wallet_address == wallet_address)
                .group_by(Portfolio.wallet_address)
            )
            res = await self._session.execute(stmt)
            row = res.one_or_none()

            if row is None:
                logger.warning(
                    "Nothing found",
                    wallet_address=wallet_address,
                )
                return None

            portfolio_model, assets_counted = row

            mapped_portfolio = self._mapper.from_database(portfolio_model)
            logger.info(
                "Assets counted & portfolio found",
                wallet_address=wallet_address,
                len_=assets_counted,
            )
            return mapped_portfolio, assets_counted

        except SQLAlchemyError as e:
            logger.error(
                "Error occurred during from database",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError(
                "Unable to load or calculate assets & portfolio information"
            ) from e

        except Exception as e:
            logger.error(
                "Unexpected error occurred during from database",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError(
                "Unable to load or calculate assets & portfolio information"
            ) from e
