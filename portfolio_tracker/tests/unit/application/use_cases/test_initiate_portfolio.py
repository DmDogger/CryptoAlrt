import pytest

from domain.entities.portfolio_entity import PortfolioEntity

from fixtures.domain_fixtures import sample_asset_entity
from helpers.mocks.repositories import fake_portfolio_repository


class TestInitiatePortfolioUseCase:
    @pytest.mark.asyncio
    async def test_empty_initiating_works_correctly(self, mock_initiate_portfolio_uc):
        res = await mock_initiate_portfolio_uc.execute(
            wallet_address="xXx_InItAdResS_xXx",
        )

        assert isinstance(res, PortfolioEntity)
        assert res.assets is None
        assert res.total_value is None
        assert res.assets_count is None

    @pytest.mark.asyncio
    async def test_non_empty_init_works_correctly(
        self, sample_asset_entity, mock_initiate_portfolio_uc
    ):
        res = await mock_initiate_portfolio_uc.execute(
            wallet_address="xXx_InItAdResS_xXx", assets=[sample_asset_entity, sample_asset_entity]
        )

        assert len(res.assets) == 2
