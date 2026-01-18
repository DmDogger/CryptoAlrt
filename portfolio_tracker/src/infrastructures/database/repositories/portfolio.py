"""Repository for portfolio database operations using SQLAlchemy.

This module provides data access layer for portfolio entities with assets and prices.
"""

from dataclasses import dataclass
from datetime import timedelta, UTC, datetime
from decimal import Decimal
from typing import final
from uuid import UUID

import structlog
from sqlalchemy import select, func, update, and_, delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructures.database.mappers.portfolio_db_mapper import PortfolioDBMapper
from domain.entities.portfolio_entity import PortfolioEntity
from infrastructures.database.models.portfolio import Portfolio
from infrastructures.database.models.cryptoprice import CryptoPrice, MarketPriceHistory
from infrastructures.database.models.asset import Asset
from sqlalchemy.orm import selectinload

from domain.entities.asset_entity import AssetEntity
from domain.exceptions import RepositoryError
from application.interfaces.repositories import PortfolioRepositoryProtocol
from domain.value_objects.analytics_vo import AnalyticsValueObject

from infrastructures.database.mappers.analytics_db_mapper import AnalyticsDBMapper

from infrastructures.database.mappers.asset_db_mapper import AssetDBMapper
from infrastructures.exceptions import DatabaseSavingError

logger = structlog.getLogger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class SQLAlchemyPortfolioRepository(PortfolioRepositoryProtocol):
    """Repository for portfolio database operations."""

    _session: AsyncSession
    _mapper: PortfolioDBMapper
    _asset_mapper: AssetDBMapper

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
                    selectinload(
                        Portfolio.assets,
                    ).selectinload(
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
        """
        try:
            logger.debug("Trying to get portfolio total_value & portfolio entity ")
            stmt = (
                select(
                    Portfolio,
                    func.sum(Asset.amount * CryptoPrice.price).label("calculated_total_value"),
                )
                .join(Asset, Asset.wallet_address == Portfolio.wallet_address)
                .join(CryptoPrice, CryptoPrice.cryptocurrency == Asset.ticker)
                .where(Portfolio.wallet_address == wallet_address)
                .group_by(Portfolio.wallet_address)
                .options(
                    selectinload(
                        Portfolio.assets,
                    ).selectinload(
                        Asset.crypto_price,
                    )
                )
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
        """Retrieve portfolio with count of associated assets."""
        try:
            logger.debug(
                "Trying to get portfolio information & assets count",
                wallet_address=wallet_address,
            )
            stmt = (
                select(Portfolio, func.count(Asset.asset_id).label("total_assets_count"))
                .join(Asset, Asset.wallet_address == Portfolio.wallet_address)
                .where(Portfolio.wallet_address == wallet_address)
                .options(
                    selectinload(
                        Portfolio.assets,
                    ).selectinload(Asset.crypto_price)
                )
                .group_by(Portfolio.wallet_address)
            )
            res = await self._session.execute(stmt)
            row = res.unique().one_or_none()

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

    async def get_portfolio_total_value_only(self, wallet_address: str) -> Decimal | None:
        try:
            stmt = (
                select(func.sum(Asset.amount * CryptoPrice.price).label("total_value"))
                .join(CryptoPrice, CryptoPrice.cryptocurrency == Asset.ticker)
                .join(Portfolio, Portfolio.wallet_address == Asset.wallet_address)
                .where(Asset.wallet_address == wallet_address)
            )
            res_obj = await self._session.execute(stmt)
            total_value = res_obj.scalar_one_or_none()

            if total_value is None:
                return None

            return Decimal(total_value)

        except SQLAlchemyError as e:
            logger.error(
                "Error occurred during from database",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError("Unable to load or calculate portfolio's total value") from e

        except Exception as e:
            logger.error(
                "Unexpected error occurred during from database",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError("Unable to load or calculate portfolio's total value") from e

    async def get_last_total_value(self, wallet_address: str, hours: int = 24) -> Decimal | None:
        """Calculate portfolio total value using last/historical prices."""
        try:
            last_price_subq = (
                select(
                    MarketPriceHistory.cryptocurrency.label("ticker"),
                    MarketPriceHistory.price.label("last_price"),
                )
                .where(
                    MarketPriceHistory.timestamp
                    >= datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=hours)
                )
                .distinct(MarketPriceHistory.cryptocurrency)
                .order_by(
                    MarketPriceHistory.cryptocurrency,
                    MarketPriceHistory.timestamp.asc(),
                )
                .subquery()
            )

            stmt = (
                select(
                    func.sum(Asset.amount * last_price_subq.c.last_price).label("last_total_value")
                )
                .select_from(Asset)
                .join(Portfolio, Portfolio.wallet_address == Asset.wallet_address)
                .join(last_price_subq, last_price_subq.c.ticker == Asset.ticker)
                .where(Asset.wallet_address == wallet_address)
            )
            res_obj = await self._session.execute(stmt)
            last_total_value = res_obj.scalar_one_or_none()

            if last_total_value is None:
                return None

            return Decimal(last_total_value)

        except SQLAlchemyError as e:
            logger.error(
                "Error occurred during from database",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError("Unable to load or calculate portfolio's last total value") from e

        except Exception as e:
            logger.error(
                "Unexpected error occurred during from database",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError("Unable to load or calculate portfolio's last total value") from e

    async def get_position_value(self, ticker: str, wallet_address: str) -> AnalyticsValueObject:
        try:
            stmt = (
                select(Asset.ticker, (Asset.amount * CryptoPrice.price).label("position_value"))
                .join(CryptoPrice, CryptoPrice.cryptocurrency == Asset.ticker)
                .where(Asset.wallet_address == wallet_address, Asset.ticker == ticker)
            )
            res_obj = await self._session.execute(stmt)
            row = res_obj.one_or_none()

            if row is None:
                return None

            return AnalyticsDBMapper.from_database(row)

        except SQLAlchemyError as e:
            logger.error(
                "Error occurred during from database",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError("Unable to calculate position value") from e

        except Exception as e:
            logger.error(
                "Unexpected error occurred during from database",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError("Unable to load or calculate portfolio's position value") from e

    async def get_position_values(self, wallet_address: str) -> None | list[AnalyticsValueObject]:
        try:
            stmt = (
                select(Asset.ticker, (Asset.amount * CryptoPrice.price).label("position_value"))
                .join(CryptoPrice, CryptoPrice.cryptocurrency == Asset.ticker)
                .where(Asset.wallet_address == wallet_address)
            )
            res_obj = await self._session.execute(stmt)
            rows = res_obj.all()

            if not rows:
                return None

            return [AnalyticsDBMapper.from_database(r) for r in rows]

        except SQLAlchemyError as e:
            logger.error(
                "Error occurred during from database",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError("Unable to calculate position value") from e

        except Exception as e:
            logger.error(
                "Unexpected error occurred during from database",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError("Unable to load or calculate portfolio's position value") from e

    async def get_portfolio_by_wallet_address(self, wallet_address: str) -> None | PortfolioEntity:
        try:
            stmt = select(Portfolio).where(Portfolio.wallet_address == wallet_address)

            res_obj = await self._session.execute(stmt)
            portfolio = res_obj.scalar_one_or_none()

            if portfolio is None:
                return None

            return self._mapper.from_database(portfolio)

        except SQLAlchemyError as e:
            logger.error(
                "Error occurred during from database",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError("Unable to get portfolio") from e

        except Exception as e:
            logger.error(
                "Unexpected error occurred during from database",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError("Unable to load portfolio") from e

    async def get_current_and_last_prices(
        self,
        ticker: str,
        hours: int = 24,
    ) -> tuple[Decimal, Decimal | None] | None:
        try:
            stmt = (
                select(
                    CryptoPrice.price.label("current_price"),
                    MarketPriceHistory.price.label("last_price"),
                )
                .join(
                    MarketPriceHistory,
                    MarketPriceHistory.cryptocurrency == CryptoPrice.cryptocurrency,
                )
                .where(
                    CryptoPrice.cryptocurrency == ticker,
                    MarketPriceHistory.timestamp
                    >= datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=hours),
                )
                .order_by(MarketPriceHistory.timestamp.asc())
                .limit(1)
            )
            res_obj = await self._session.execute(stmt)
            prices_row = res_obj.one_or_none()

            if prices_row is None:
                return None

            current_price, last_price = prices_row
            return current_price, last_price

        except SQLAlchemyError as e:
            logger.error(
                "Error occurred during from database",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError("Unable to load prices") from e

        except Exception as e:
            logger.error(
                "Unexpected error occurred during from database",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError("Unable to load prices") from e

    async def get_assets_counted(self, wallet_address: str) -> int | None:
        try:
            stmt = select(func.count(Asset.asset_id)).where(Asset.wallet_address == wallet_address)
            res = await self._session.execute(stmt)
            assets_counted = res.scalar_one_or_none()

            return assets_counted

        except SQLAlchemyError as e:
            logger.error(
                "Error occurred during from database",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError("Unable to load prices") from e

        except Exception as e:
            logger.error(
                "Unexpected error occurred during from database",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError("Unable to load prices") from e

    async def save_portfolio(self, portfolio_entity: PortfolioEntity) -> PortfolioEntity:
        """Save a new portfolio entity to the database."""
        try:
            logger.debug(
                "Saving portfolio to database",
                wallet_address=portfolio_entity.wallet_address,
            )
            portfolio_model = self._mapper.to_database(portfolio_entity)
            self._session.add(portfolio_model)
            await self._session.commit()

            logger.debug(
                "Portfolio successfully saved to database",
                wallet_address=portfolio_entity.wallet_address,
            )
            return portfolio_entity

        except IntegrityError as e:
            await self._session.rollback()
            logger.error(
                "Database constraint violation occurred during portfolio saving",
                error=str(e),
                error_type=type(e).__name__,
                wallet_address=portfolio_entity.wallet_address,
                exc_info=True,
            )
            raise DatabaseSavingError(
                f"Failed to save portfolio: constraint violation - {str(e)}"
            ) from e

        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(
                "SQLAlchemy error occurred while saving portfolio",
                error=str(e),
                error_type=type(e).__name__,
                wallet_address=portfolio_entity.wallet_address,
                exc_info=True,
            )
            raise DatabaseSavingError(f"Failed to save portfolio to database: {str(e)}") from e

        except Exception as e:
            await self._session.rollback()
            logger.error(
                "Unexpected error occurred while saving portfolio",
                error=str(e),
                error_type=type(e).__name__,
                wallet_address=portfolio_entity.wallet_address,
                exc_info=True,
            )
            raise DatabaseSavingError(
                f"Unexpected error occurred while saving portfolio: {str(e)}"
            ) from e

    async def update_portfolio(self, portfolio_entity: PortfolioEntity) -> PortfolioEntity:
        """Update an existing portfolio entity in the database."""
        try:
            logger.debug(
                "Updating portfolio in database",
                wallet_address=portfolio_entity.wallet_address,
            )

            update_dict = PortfolioDBMapper.to_dict(portfolio_entity)

            stmt = (
                update(Portfolio)
                .where(Portfolio.wallet_address == portfolio_entity.wallet_address)
                .values(update_dict)
                .returning(Portfolio)
            )
            result = await self._session.execute(stmt)
            updated_portfolio = result.unique().scalar_one_or_none()

            if updated_portfolio is None:
                await self._session.rollback()
                logger.error(
                    "Portfolio not found for update",
                    wallet_address=portfolio_entity.wallet_address,
                )
                raise DatabaseSavingError(
                    f"Portfolio with wallet address {portfolio_entity.wallet_address} not found"
                )

            await self._session.commit()

            logger.debug(
                "Portfolio successfully updated in database",
                wallet_address=portfolio_entity.wallet_address,
            )
            return portfolio_entity

        except IntegrityError as e:
            await self._session.rollback()
            logger.error(
                "Database constraint violation occurred during portfolio update",
                error=str(e),
                error_type=type(e).__name__,
                wallet_address=portfolio_entity.wallet_address,
                exc_info=True,
            )
            raise DatabaseSavingError(
                f"Failed to update portfolio: constraint violation - {str(e)}"
            ) from e

        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(
                "SQLAlchemy error occurred while updating portfolio",
                error=str(e),
                error_type=type(e).__name__,
                wallet_address=portfolio_entity.wallet_address,
                exc_info=True,
            )
            raise DatabaseSavingError(f"Failed to update portfolio in database: {str(e)}") from e

        except Exception as e:
            await self._session.rollback()
            logger.error(
                "Unexpected error occurred while updating portfolio",
                error=str(e),
                error_type=type(e).__name__,
                wallet_address=portfolio_entity.wallet_address,
                exc_info=True,
            )
            raise DatabaseSavingError(
                f"Unexpected error occurred while updating portfolio: {str(e)}"
            ) from e

    async def add_asset(self, asset_entity: AssetEntity) -> AssetEntity:
        try:
            db_asset = self._asset_mapper.to_database(asset_entity)
            self._session.add(db_asset)
            await self._session.commit()
            await self._session.refresh(db_asset)
            return self._asset_mapper.from_database(db_asset)

        except IntegrityError as e:
            await self._session.rollback()
            logger.error(
                "Database constraint violation occurred during saving asset",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise DatabaseSavingError(
                f"Failed to add asset: constraint violation - {str(e)}"
            ) from e

        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(
                "SQLAlchemy error occurred while saving asset",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise DatabaseSavingError(f"Failed to save asset in database: {str(e)}") from e

        except Exception as e:
            await self._session.rollback()
            logger.error(
                "Unexpected error occurred while saving asset",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise DatabaseSavingError(
                f"Unexpected error occurred while saving asset: {str(e)}"
            ) from e

    async def get_asset_by_id(self, asset_id: UUID) -> AssetEntity | None:
        try:
            stmt = select(Asset).where(Asset.asset_id == asset_id)
            res_obj = await self._session.execute(stmt)
            asset = res_obj.scalar_one_or_none()

            if asset is None:
                return None

            return self._asset_mapper.from_database(asset)

        except SQLAlchemyError as e:
            logger.error(
                "SQLAlchemy error occurred while retrieve asset",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError("Occurred error during retrieving asset") from e

        except Exception as e:
            logger.error(
                "Unexpected error occurred while retrieving asset",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise RepositoryError("Occurred error during retrieving asset") from e

    async def update_asset(self, asset_entity: AssetEntity) -> AssetEntity | None:
        try:
            stmt = (
                update(Asset)
                .where(Asset.wallet_address == asset_entity.wallet_address)
                .values(self._asset_mapper.to_dict(asset_entity))
                .returning(Asset)
            )

            result = await self._session.execute(stmt)
            asset = result.unique().scalar_one_or_none()

            if asset is None:
                await self._session.rollback()
                return None

            return self._asset_mapper.from_database(asset)

        except IntegrityError as e:
            await self._session.rollback()
            logger.error(
                "Database constraint violation occurred during asset update",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise DatabaseSavingError(
                f"Failed to update asset: constraint violation - {str(e)}"
            ) from e

        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(
                "SQLAlchemy error occurred while updating asset",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise DatabaseSavingError(f"Failed to update asset in database: {str(e)}") from e

        except Exception as e:
            await self._session.rollback()
            logger.error(
                "Unexpected error occurred while updating asset",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise DatabaseSavingError(
                f"Unexpected error occurred while updating asset: {str(e)}"
            ) from e

    async def delete_asset(self, asset_id: UUID) -> AssetEntity | None:
        try:
            stmt = delete(Asset).where(Asset.asset_id == asset_id).returning(Asset)
            res_obj = await self._session.execute(stmt)
            deleted = res_obj.scalar_one_or_none()

            if deleted is None:
                return None

            await self._session.commit()
            return self._asset_mapper.from_database(deleted)

        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(
                "SQLAlchemy error occurred while deleting asset",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise DatabaseSavingError(f"Failed to delete asset from database: {str(e)}") from e

        except Exception as e:
            await self._session.rollback()
            logger.error(
                "Unexpected error occurred while deleting asset",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise DatabaseSavingError(
                f"Unexpected error occurred while deleting asset: {str(e)}"
            ) from e
