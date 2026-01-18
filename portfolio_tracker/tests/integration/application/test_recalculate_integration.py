from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fixtures.infra_fixtures import portfolio_repository_for_transactions

from domain.entities.portfolio_entity import PortfolioEntity

if TYPE_CHECKING:
    from application.use_cases.recalculate_portfolio_change import RecalculatePortfolioChangeUseCase
    from infrastructures.database.repositories.portfolio import SQLAlchemyPortfolioRepository


class TestRecalculateUCIntegration:
    @pytest.mark.asyncio
    async def test_recalculating_works_correctly_integration(
        self,
        fill_integration_base_fields: None,
        async_session: AsyncSession,
        integration_portfolio_entity: PortfolioEntity,
        portfolio_repository_for_transactions: "SQLAlchemyPortfolioRepository",
        recalculating_uc_integration: "RecalculatePortfolioChangeUseCase",
    ) -> None:

        await portfolio_repository_for_transactions.save_portfolio(integration_portfolio_entity)

        await async_session.commit()

        percent = await recalculating_uc_integration.execute(
            wallet_address=integration_portfolio_entity.wallet_address
        )

        assert percent is not None
        assert isinstance(percent, Decimal)
