"""Analytics service for portfolio calculations and metrics."""

from decimal import Decimal


class AnalyticsService:
    """Service providing analytics calculations for portfolio management.

    This service contains static methods for calculating portfolio metrics
    such as price changes and asset allocation percentages.
    """

    @staticmethod
    def portfolio_change(last_price: Decimal, current_price: Decimal) -> Decimal:
        """Calculate percentage change between two prices.

        Args:
            last_price: Previous price value.
            current_price: Current price value.

        Returns:
            Percentage change as Decimal (can be negative for losses).

        Example:
            >>> AnalyticsService.portfolio_change(Decimal("100"), Decimal("110"))
            Decimal('10.0')
        """
        return ((current_price - last_price) / last_price) * 100

    @staticmethod
    def calculate_allocation(asset_value: Decimal, total_value: Decimal) -> Decimal:
        """Calculate asset allocation percentage in portfolio.

        Args:
            asset_value: Value of a single asset.
            total_value: Total value of the entire portfolio.

        Returns:
            Allocation percentage as Decimal (0-100).

        Example:
            >>> AnalyticsService.calculate_allocation(Decimal("50"), Decimal("200"))
            Decimal('25.0')
        """
        return (asset_value / total_value) * 100
