from decimal import Decimal

import pytest

from domain.entities.portfolio_entity import PortfolioEntity

from application.use_cases.calculate_weight import CalculateWeightUseCase

from application.exceptions import UseCaseError
from domain.exceptions import RepositoryError
from fixtures.domain_fixtures import sample_portfolio_entity


class TestCalculateWeightUseCase:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "asset_amount, portfolio_total_value",
        [
            (Decimal("5"), Decimal("100")),
            (Decimal("0.00001"), Decimal("103")),
            (Decimal("999999"), Decimal("100000")),
            (Decimal("0.05"), Decimal("999999")),
        ],
    )
    async def test_calculate_weight_uc_works_correctly(
        self,
        asset_amount: Decimal,
        portfolio_total_value: Decimal,
        mock_calculate_weight_uc: CalculateWeightUseCase,
        sample_portfolio_entity: PortfolioEntity,
        fill_portfolio_repository: "PortfolioRepositoryFiller",
    ):

        await fill_portfolio_repository.setup_for_calculate_weight(
            wallet_address=sample_portfolio_entity.wallet_address,
            ticker="BTC",
            asset_amount=asset_amount,
            crypto_price=90_000,
            portfolio_total_value=portfolio_total_value,
        )

        obj = await mock_calculate_weight_uc.execute(
            ticker="BTC",
            wallet_address=sample_portfolio_entity.wallet_address,
        )

        assert obj is not None
        assert obj > 0.01
        assert isinstance(obj, Decimal)

    async def test_uc_raises_errors_correctly(
        self,
        mock_calculate_weight_uc: CalculateWeightUseCase,
    ):
        with pytest.raises(UseCaseError):
            await mock_calculate_weight_uc.execute(
                ticker="BTC",
                wallet_address="wallet_",
            )
