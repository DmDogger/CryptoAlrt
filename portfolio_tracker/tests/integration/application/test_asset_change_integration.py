from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

import application.exceptions

if TYPE_CHECKING:
    from application.use_cases.calculate_asset_change import CalculateAssetChangeUseCase


class TestCalculateAssetChangeIntegration:
    @pytest.mark.asyncio
    async def test_calculate_asset_change_uc_works_correctly(
        self,
        asset_change_uc_integration: "CalculateAssetChangeUseCase",
        fill_prices_only: None,
        async_session: AsyncSession,
    ) -> None:
        await async_session.commit()

        percent = await asset_change_uc_integration.execute(ticker="BTC")

        assert percent is not None
        assert isinstance(percent, Decimal)
        assert percent >= 5

    @pytest.mark.asyncio
    async def test_use_case_raises_error_correctly(
        self, asset_change_uc_integration: "CalculateAssetChangeUseCase"
    ) -> None:
        with pytest.raises(application.exceptions.UseCaseError):
            await asset_change_uc_integration.execute(ticker="NO_COIN")
