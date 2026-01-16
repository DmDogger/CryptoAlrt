import pytest

from application.use_cases.calculate_portfolio_change import CalculateAssetChangeUseCase

from helpers.mocks.repositories import fake_portfolio_repository


@pytest.fixture
def mock_calculate_asset_change_uc(fake_portfolio_repository):
    return CalculateAssetChangeUseCase(repository=fake_portfolio_repository)


@pytest.fixture
async def asset_change_uc_integration(portfolio_repository_for_transactions):
    return CalculateAssetChangeUseCase(repository=portfolio_repository_for_transactions)
