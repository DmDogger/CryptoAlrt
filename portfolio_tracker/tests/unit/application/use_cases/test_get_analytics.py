from decimal import Decimal

import pytest

from domain.value_objects.analytics_vo import AnalyticsValueObject
from fixtures.domain_fixtures import sample_portfolio_entity


class TestGetAnalyticsUseCase:
    @pytest.mark.asyncio
    async def test_uc_works_correctly(
        self, fake_portfolio_repository, mock_get_analytics_uc, sample_portfolio_entity
    ):
        await fake_portfolio_repository.save_portfolio(sample_portfolio_entity)

        fake_portfolio_repository.add_crypto_price("BTC", Decimal("103000"))
        fake_portfolio_repository.add_price_history("BTC", Decimal("13000"))

        res = await mock_get_analytics_uc.execute(
            wallet_address=sample_portfolio_entity.wallet_address
        )

        assert res is not None
        assert all(isinstance(r, AnalyticsValueObject) for r in res)
        assert len(res) > 0
