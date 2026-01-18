"""Analytics service for portfolio calculations and metrics."""

from decimal import Decimal

from domain.exceptions import DomainValidationError


class AnalyticsService:
    @staticmethod
    def portfolio_change(last_price: Decimal, current_price: Decimal) -> Decimal:
        """Calculate percentage change between two prices.

        Args:
            last_price: Previous price value.
            current_price: Current price value.

        Returns:
            Percentage change as Decimal.

        Raises:
            DomainValidationError: If last_price is zero.
        """
        try:
            return ((current_price - last_price) / last_price) * 100
        except ZeroDivisionError:
            raise DomainValidationError(
                "Last price cannot be zero for portfolio change calculation"
            )

    @staticmethod
    def calculate_allocation(asset_value: Decimal, total_value: Decimal) -> Decimal:
        """Calculate asset allocation percentage in portfolio.

        Args:
            asset_value: Value of the specific asset position.
            total_value: Total value of the entire portfolio.

        Returns:
            Allocation percentage as Decimal (0-100).

        Raises:
            DomainValidationError: If total_value is zero.
        """
        try:
            return (asset_value / total_value) * 100
        except ZeroDivisionError:
            raise DomainValidationError("Total value cannot be zero for allocation calculation")
