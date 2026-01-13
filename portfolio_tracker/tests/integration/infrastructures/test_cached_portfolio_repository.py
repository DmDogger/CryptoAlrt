from decimal import Decimal

import pytest
import redis.exceptions

from domain.entities.portfolio_entity import PortfolioEntity
from infrastructures.database.repositories.cached_portfolio_repository import (
    CachedPortfolioRepository,
)

from fixtures.infra_fixtures import async_session


class TestCachedPortfolioRepository:
    @pytest.mark.asyncio
    async def test_get_portfolio_with_fields_from_cache(
        self,
        sample_empty_portfolio_entity: PortfolioEntity,
        mock_cached_portfolio_repository: CachedPortfolioRepository,
    ) -> None:
        """Test that cached repository correctly retrieves portfolio with optional None fields."""
        await mock_cached_portfolio_repository._original.save_portfolio(
            sample_empty_portfolio_entity
        )
        res = await mock_cached_portfolio_repository.get_portfolio_with_assets_and_prices(
            wallet_address=sample_empty_portfolio_entity.wallet_address
        )

        assert isinstance(res, PortfolioEntity)
        assert None in [res.assets, res.weight, res.total_value]

    @pytest.mark.asyncio
    async def test_get_portfolio_with_total_value(
        self,
        sample_portfolio_entity: PortfolioEntity,
        mock_cached_portfolio_repository: CachedPortfolioRepository,
    ) -> None:

        await mock_cached_portfolio_repository._original.save_portfolio(sample_portfolio_entity)

        portfolio, total_value = await mock_cached_portfolio_repository.get_portfolio_total_value(
            sample_portfolio_entity.wallet_address
        )

        assert total_value is not None
        assert isinstance(portfolio, PortfolioEntity)
        assert isinstance(total_value, Decimal)

    @pytest.mark.asyncio
    async def test_get_portfolio_with_assets_count(
        self, async_session, mock_cached_portfolio_repository, sample_custom_portfolio_entity
    ):

        portfolio = sample_custom_portfolio_entity(asset_counted=2, asset_counts=2)

        await mock_cached_portfolio_repository._original.save_portfolio(portfolio)

        await async_session.commit()

        portfolio, assets_count = (
            await mock_cached_portfolio_repository.get_portfolio_with_assets_count(
                portfolio.wallet_address
            )
        )

        assert isinstance(assets_count, int)
        assert assets_count == 2
        assert isinstance(portfolio, PortfolioEntity)

    @pytest.mark.asyncio
    async def test_raises_dataerror(self, sample_portfolio_entity, full_mocked_cached_repository):

        full_mocked_cached_repository._original.get_portfolio_with_assets_count.side_effect = (
            redis.exceptions.DataError
        )

        with pytest.raises(redis.exceptions.DataError):
            await full_mocked_cached_repository.get_portfolio_with_assets_count("wallet_address")

            full_mocked_cached_repository._original.get_portfolio_with_assets_and_prices.assert_called_once()
