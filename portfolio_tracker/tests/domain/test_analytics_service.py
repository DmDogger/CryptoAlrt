from decimal import Decimal

from domain.services.analytics_service import AnalyticsService


class TestDomainAnalyticsService:
    def test_portfolio_change(self):
        res = AnalyticsService.portfolio_change(
            last_price=Decimal("100"), current_price=Decimal("10")
        )

        assert res == Decimal("-90.0")

    def test_calculate_allocation(self):
        res = AnalyticsService.calculate_allocation(
            asset_value=Decimal("150"),
            total_value=Decimal("1500"),
        )

        assert res == Decimal("10")
