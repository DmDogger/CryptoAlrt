import pytest

from domain.value_objects.analytics_vo import AnalyticsValueObject


class TestGetAnalyticsIntegration:
    @pytest.mark.asyncio
    async def test_get_analytics_uc_works_correct(
        self, fill_integration_base_data: None, integration_portfolio_entity, get_analytics_uc_integration
    ):
        res = await get_analytics_uc_integration.execute(integration_portfolio_entity.wallet_address)

        assert all(isinstance(r, AnalyticsValueObject) for r in res)
        assert len(res) > 0
