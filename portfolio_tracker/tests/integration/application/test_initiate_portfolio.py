from decimal import Decimal

import pytest
from typing import TYPE_CHECKING

from domain.entities.portfolio_entity import PortfolioEntity

from fixtures.domain_fixtures import sample_asset_entity

if TYPE_CHECKING:
    from application.use_cases.initiate_portfolio import InitiatePortfolioUseCase
    from domain.entities.asset_entity import AssetEntity


class TestInitiatePortfolioUseCaseIntegration:
    @pytest.mark.asyncio
    async def test_init_empty_portfolio_uc_integration(
        self, initiate_portfolio_uc: "InitiatePortfolioUseCase"
    ) -> None:

        res = await initiate_portfolio_uc.execute(wallet_address="0x123")

        assert res.assets is None
        assert isinstance(res, PortfolioEntity)

    @pytest.mark.asyncio
    async def test_init_non_empty_portfolio_uc_integration(
        self, initiate_portfolio_uc: "InitiatePortfolioUseCase", fill_btc_eth_prices
    ) -> None:

        assets = [
            AssetEntity.create(
                ticker=ticker,
                amount=Decimal("0.0005"),
                wallet_address="0x!23",
            )
            for ticker in ["BTC", "ETH"]
        ]

        res = await initiate_portfolio_uc.execute(
            wallet_address="0x!23",
            assets=assets,
        )

        assert res.assets is not None
        assert len(res.assets) == 2
