from decimal import Decimal

import pytest

from infrastructures.database.repositories.portfolio import SQLAlchemyPortfolioRepository

from application.exceptions import UseCaseError


class TestCalculatePortfolioUseCase:
    @pytest.mark.asyncio
    async def test_use_case_works_correctly(
        self,
        fake_portfolio_repository: "SQLAlchemyPortfolioRepository",
        mock_calculate_asset_change_uc: "CalculatePortfolioUseCase",
    ) -> None:
        # In a real repository, we fetch this data from "price_tracking_service".
        # These methods do not originally exist; they are provided only for testing this UC.
        fake_portfolio_repository.add_crypto_price("BTC", Decimal("100000"))
        fake_portfolio_repository.add_price_history("BTC", Decimal("95000"))

        percent = await mock_calculate_asset_change_uc.execute(ticker="BTC")

        assert percent is not None
        assert isinstance(percent, Decimal)
        assert percent >= 5

    @pytest.mark.asyncio
    async def test_use_case_raises_error_correctly(
        self,
        mock_calculate_asset_change_uc: "CalculatePortfolioUseCase",
    ) -> None:
        with pytest.raises(UseCaseError):
            await mock_calculate_asset_change_uc.execute(ticker="BTC")
