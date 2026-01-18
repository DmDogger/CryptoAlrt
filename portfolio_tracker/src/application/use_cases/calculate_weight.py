from datetime import datetime, UTC

import structlog
from application.exceptions import UseCaseError, TotalValueUnableToCalculate, AnalyticsDataIsEmpty
from application.interfaces import PortfolioRepositoryProtocol
from domain.value_objects.analytics_vo import AnalyticsValueObject

from domain.exceptions import RepositoryError
from domain.services.analytics_service import AnalyticsService

logger = structlog.getLogger(__name__)


class CalculateWeightUseCase:
    """Use case for calculating asset allocation weight in portfolio."""

    def __init__(self, repository: PortfolioRepositoryProtocol):
        self._repository = repository

    async def execute(self, ticker: str, wallet_address: str) -> AnalyticsValueObject:
        """Calculate asset allocation percentage in portfolio.

        Args:
            ticker: Cryptocurrency ticker symbol.
            wallet_address: Wallet address to find portfolio.

        Returns:
            AnalyticsValueObject with calculated allocation percentage.

        Raises:
            UseCaseError: If calculation fails or data is invalid.
        """
        try:
            total_value = await self._repository.get_portfolio_total_value_only(
                wallet_address=wallet_address
            )

            if total_value is None:
                logger.error(
                    "",
                    ticker=ticker,
                    wallet_address=wallet_address,
                )
                raise TotalValueUnableToCalculate(
                    f"Total value unable to calculate for ticker: {ticker}, wallet address: {wallet_address}"
                )

            analytics_object = await self._repository.get_position_value(
                wallet_address=wallet_address, ticker=ticker
            )

            if analytics_object is None or analytics_object.position_value is None:
                logger.error("", ticker=ticker, wallet_address=wallet_address)
                raise AnalyticsDataIsEmpty(
                    f"Unable to find position value field in analytics object for ticker: {ticker} and wallet address: {wallet_address} "
                )

            return AnalyticsService.calculate_allocation(
                asset_value=analytics_object.position_value, total_value=total_value
            )

        except (RepositoryError, TotalValueUnableToCalculate, AnalyticsDataIsEmpty) as e:
            logger.error(
                "Operation failed",
                error_type=type(e).__name__,
                error=str(e),
                timestamp=datetime.now(UTC),
            )
            raise UseCaseError("Occurred error during calculation asset weight") from e

        except Exception as e:
            logger.error(
                "Operation failed",
                error_type=type(e).__name__,
                error=str(e),
                timestamp=datetime.now(UTC),
            )
            raise UseCaseError("Occurred unexpected error during calculation assets weight") from e
