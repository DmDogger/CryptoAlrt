from unittest.mock import AsyncMock

import pytest

from application.use_cases.calculate_weight import CalculateWeightUseCase
from infrastructures.database.repositories.portfolio import SQLAlchemyPortfolioRepository
from application.use_cases.recalculate_portfolio_change import RecalculatePortfolioChangeUseCase
from application.use_cases.initiate_portfolio import InitiatePortfolioUseCase


@pytest.fixture
def mock_calculate_weight_uc(
    fake_portfolio_repository: "SQLAlchemyPortfolioRepository",
) -> CalculateWeightUseCase:
    return CalculateWeightUseCase(
        repository=fake_portfolio_repository,
    )


@pytest.fixture
def mock_full_mocked_calculate_weight_uc() -> CalculateWeightUseCase:
    return CalculateWeightUseCase(
        repository=AsyncMock(spec=SQLAlchemyPortfolioRepository),
    )


@pytest.fixture
def mock_recalculate_portfolio_uc(fake_portfolio_repository) -> RecalculatePortfolioChangeUseCase:
    return RecalculatePortfolioChangeUseCase(
        repository=fake_portfolio_repository,
    )


@pytest.fixture
def mock_initiate_portfolio_uc(fake_portfolio_repository):
    return InitiatePortfolioUseCase(
        repository=fake_portfolio_repository,
    )
