from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from domain.entities.asset_entity import AssetEntity
from fixtures.domain_fixtures import sample_asset_entity

if TYPE_CHECKING:
    from application.use_cases.initiate_portfolio import InitiatePortfolioUseCase
    from application.use_cases.change_asset_amount import ChangeAssetAmountUseCase


class TestChangeAssetAmountUseCase:
    @pytest.mark.asyncio
    async def test_change_asset_uc(
        self,
        initiate_portfolio_uc: "InitiatePortfolioUseCase",
        sample_asset_entity: AssetEntity,
        unique_wallet_address: str,
        change_asset_uc: "ChangeAssetAmountUseCase",
    ) -> None:

        await initiate_portfolio_uc.execute(
            wallet_address=unique_wallet_address,
            assets=[
                AssetEntity.create(
                    wallet_address=unique_wallet_address,
                    ticker="BTC",
                    amount=Decimal("0"),
                )
            ],
        )

        updated = await change_asset_uc.execute(
            wallet_address=unique_wallet_address,
            ticker="BTC",
            amount=Decimal("5"),
        )

        assert updated.amount == Decimal("5")
        assert updated.ticker == "BTC"
        assert updated.wallet_address == unique_wallet_address
