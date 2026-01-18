import pytest

from application.use_cases.calculate_asset_change import CalculateAssetChangeUseCase
from application.use_cases.recalculate_portfolio_change import RecalculatePortfolioChangeUseCase

from application.use_cases.initiate_portfolio import InitiatePortfolioUseCase

from application.use_cases.change_asset_amount import ChangeAssetAmountUseCase


@pytest.fixture
def mock_calculate_asset_change_uc(fake_portfolio_repository):
    return CalculateAssetChangeUseCase(repository=fake_portfolio_repository)


@pytest.fixture
async def asset_change_uc_integration(portfolio_repository_for_transactions):
    return CalculateAssetChangeUseCase(repository=portfolio_repository_for_transactions)


@pytest.fixture
async def recalculating_uc_integration(portfolio_repository_for_transactions):
    return RecalculatePortfolioChangeUseCase(repository=portfolio_repository_for_transactions)


@pytest.fixture
async def initiate_portfolio_uc(portfolio_repository_for_transactions):
    return InitiatePortfolioUseCase(repository=portfolio_repository_for_transactions)


@pytest.fixture
async def change_asset_uc(portfolio_repository_for_transactions):
    return ChangeAssetAmountUseCase(repository=portfolio_repository_for_transactions)
