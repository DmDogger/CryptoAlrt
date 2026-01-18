from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from fixtures.infra_fixtures import portfolio_repository_for_transactions


class TestRecalculateUCIntegration:
    async def test_recalculating_works_correctly_integration(
        self,
        fill_integration_base_fields: None,
        async_session: AsyncSession,
        integration_portfolio_entity,
        portfolio_repository_for_transactions,
        recalculating_uc_integration,
    ):

        await portfolio_repository_for_transactions.save_portfolio(integration_portfolio_entity)

        await async_session.commit()

        percent = await recalculating_uc_integration.execute(
            wallet_address=integration_portfolio_entity.wallet_address
        )

        assert percent is not None
        assert isinstance(percent, Decimal)
