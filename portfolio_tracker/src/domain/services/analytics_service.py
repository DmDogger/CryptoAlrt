"""Analytics service for portfolio calculations and metrics."""

from decimal import Decimal


class AnalyticsService:
    @staticmethod
    def portfolio_change(last_price: Decimal, current_price: Decimal) -> Decimal:
        """Calculate percentage change between two prices."""
        return ((current_price - last_price) / last_price) * 100

    @staticmethod
    def calculate_allocation(asset_value: Decimal, total_value: Decimal) -> Decimal:
        """Calculate asset allocation percentage in portfolio."""
        return (asset_value / total_value) * 100
