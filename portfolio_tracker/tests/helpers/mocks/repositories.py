from decimal import Decimal

import pytest
import pytest_asyncio
from infrastructures.database.repositories.cached_portfolio_repository import (
    CachedPortfolioRepository,
)

from application.interfaces import PortfolioRepositoryProtocol
from domain.entities.asset_entity import AssetEntity
from domain.entities.portfolio_entity import PortfolioEntity
from helpers.fakes.fake_portfolio_repository import FakePortfolioRepository
from infrastructures.cache.redis import RedisCache
from infrastructures.database.mappers.portfolio_db_mapper import PortfolioDBMapper


@pytest.fixture
def fake_portfolio_repository():
    return FakePortfolioRepository()


@pytest.fixture
async def fill_portfolio_repository(fake_portfolio_repository):
    """Fixture providing helper methods to fill repository with test data."""

    class PortfolioRepositoryFiller:
        """Helper class for filling fake portfolio repository with test data."""

        def __init__(self, repo: FakePortfolioRepository):
            self._repo = repo

        async def add_portfolio(
            self,
            wallet_address: str,
            assets: list[AssetEntity] | None = None,
            total_value: Decimal | None = None,
        ) -> PortfolioEntity:
            """Add portfolio to repository.

            Args:
                wallet_address: Wallet address for the portfolio.
                assets: List of assets in the portfolio.
                total_value: Total value of the portfolio.

            Returns:
                Created PortfolioEntity.
            """
            portfolio = PortfolioEntity.create(
                wallet_address=wallet_address,
                assets=assets,
            )
            if total_value is not None:
                portfolio = portfolio.set_total_value(total_value)
            return await self._repo.save_portfolio(portfolio)

        async def add_asset_to_portfolio(
            self,
            wallet_address: str,
            ticker: str,
            amount: Decimal,
        ) -> PortfolioEntity:
            """Add asset to existing portfolio or create new one.

            Args:
                wallet_address: Wallet address for the portfolio.
                ticker: Cryptocurrency ticker symbol.
                amount: Amount of the asset.

            Returns:
                Updated PortfolioEntity.
            """
            portfolio = await self._repo.get_portfolio_with_assets_and_prices(wallet_address)
            if portfolio is None:
                asset = AssetEntity.create(
                    ticker=ticker,
                    amount=amount,
                    wallet_address=wallet_address,
                )
                portfolio = PortfolioEntity.create(
                    wallet_address=wallet_address,
                    assets=[asset],
                )
            else:
                existing_assets = list(portfolio.assets) if portfolio.assets else []
                new_asset = AssetEntity.create(
                    ticker=ticker,
                    amount=amount,
                    wallet_address=wallet_address,
                )
                existing_assets.append(new_asset)
                portfolio = PortfolioEntity(
                    wallet_address=portfolio.wallet_address,
                    assets=existing_assets,
                    total_value=portfolio.total_value,
                    weight=portfolio.weight,
                    portfolio_total=portfolio.portfolio_total,
                    assets_count=portfolio.assets_count,
                    updated_at=portfolio.updated_at,
                )
            return await self._repo.save_portfolio(portfolio)

        def add_crypto_price(self, ticker: str, price: Decimal) -> None:
            """Add cryptocurrency price.

            Args:
                ticker: Cryptocurrency ticker symbol.
                price: Current price.
            """
            self._repo.add_crypto_price(ticker, price)

        def add_price_history(self, ticker: str, price: Decimal) -> None:
            """Add historical price for cryptocurrency.

            Args:
                ticker: Cryptocurrency ticker symbol.
                price: Historical price.
            """
            self._repo.add_price_history(ticker, price)

        async def set_portfolio_total_value(
            self,
            wallet_address: str,
            total_value: Decimal,
        ) -> PortfolioEntity:
            portfolio = await self._repo.get_portfolio_with_assets_and_prices(wallet_address)
            if portfolio is None:
                raise ValueError(f"Portfolio with address {wallet_address} not found")
            portfolio = portfolio.set_total_value(total_value)
            return await self._repo.update_portfolio(portfolio)

        async def setup_for_calculate_weight(
            self,
            wallet_address: str,
            ticker: str,
            asset_amount: Decimal,
            crypto_price: Decimal,
            portfolio_total_value: Decimal | None = None,
        ) -> None:
            await self.add_asset_to_portfolio(wallet_address, ticker, asset_amount)
            self.add_crypto_price(ticker, crypto_price)

            if portfolio_total_value is None:
                portfolio_total_value = asset_amount * crypto_price

            await self.set_portfolio_total_value(wallet_address, portfolio_total_value)

        async def setup_for_recalculate_portfolio_change(
            self,
            wallet_address: str,
            ticker: str,
            asset_amount: Decimal,
            current_price: Decimal,
            last_price: Decimal,
            portfolio_total_value: Decimal | None = None,
        ) -> None:
            """Setup repository data for recalculate_portfolio_change use case."""
            await self.add_asset_to_portfolio(wallet_address, ticker, asset_amount)
            self.add_crypto_price(ticker, current_price)
            self.add_price_history(ticker, last_price)

            if portfolio_total_value is None:
                portfolio_total_value = asset_amount * current_price

            await self.set_portfolio_total_value(wallet_address, portfolio_total_value)

    return PortfolioRepositoryFiller(fake_portfolio_repository)


@pytest_asyncio.fixture
async def mock_cached_portfolio_repository(mock_redis_client, fake_portfolio_repository):
    return CachedPortfolioRepository(
        _redis_client=RedisCache(client=mock_redis_client),
        _original=fake_portfolio_repository,
        _mapper=PortfolioDBMapper(),
    )
