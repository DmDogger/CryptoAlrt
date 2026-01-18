from decimal import Decimal

import pytest

from application.use_cases.recalculate_portfolio_change import RecalculatePortfolioChangeUseCase

from application.exceptions import UseCaseError


class TestRecalculatePortfolioChange:
    @pytest.mark.asyncio
    async def test_recalculating_raises_error(
        self, mock_recalculate_portfolio_uc: RecalculatePortfolioChangeUseCase
    ):
        with pytest.raises(UseCaseError):
            await mock_recalculate_portfolio_uc.execute(wallet_address="3")

    @pytest.mark.asyncio
    async def test_recalculations_works_correctly(
        self,
        mock_recalculate_portfolio_uc: RecalculatePortfolioChangeUseCase,
        fill_portfolio_repository: None,
    ):
        await fill_portfolio_repository.setup_for_recalculate_portfolio_change(
            wallet_address="0x111",
            ticker="SOL",
            asset_amount=Decimal("1"),
            current_price=Decimal("100"),
            last_price=Decimal("98"),
            portfolio_total_value=Decimal("104"),
        )

        perc = await mock_recalculate_portfolio_uc.execute(wallet_address="0x111")

        assert perc is not None
        assert perc >= 2
        assert isinstance(perc, Decimal)
