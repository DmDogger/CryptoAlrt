"""Use case for calculating portfolio change percentage."""

from datetime import datetime, UTC
from decimal import Decimal

import structlog
from application.exceptions import CurrentPriceNotExist, HistoricalPriceError, UseCaseError
from application.interfaces import PortfolioRepositoryProtocol
from domain.services.analytics_service import AnalyticsService

from domain.exceptions import RepositoryError

logger = structlog.getLogger(__name__)


class CalculateAssetChangeUseCase:
    """Use case for calculating percentage change in asset price."""

    def __init__(self, repository: PortfolioRepositoryProtocol):
        """Initialize the use case with a repository."""
        self._repository = repository

    async def execute(self, ticker: str) -> Decimal:
        """Calculate percentage change in asset price for given ticker."""
        try:

            row = await self._repository.get_current_and_last_prices(ticker=ticker)

            if row is None:
                logger.error(
                    "Cannot to find information in database",
                    ticker=ticker,
                )
                raise HistoricalPriceError(f"Historical data not exist for ticker: {ticker}")

            current_price, last_price = row

            if current_price is None:
                logger.error(
                    "Cannot find current price for ticker",
                    ticker=ticker,
                )
                raise CurrentPriceNotExist(f"Current price not exist for ticker: {ticker}")

            port_change = AnalyticsService.portfolio_change(
                last_price=last_price if last_price is not None else current_price,
                current_price=current_price,
            )

            return port_change
        except (RepositoryError, HistoricalPriceError, CurrentPriceNotExist) as e:
            logger.error(
                "Operation failed",
                error_type=type(e).__name__,
                error=str(e),
                timestamp=datetime.now(UTC),
            )
            raise UseCaseError("Occurred error during calculation assets change percent") from e

        except Exception as e:
            logger.error(
                "Operation failed",
                error_type=type(e).__name__,
                error=str(e),
                timestamp=datetime.now(UTC),
            )
            raise UseCaseError(
                "Occurred unexpected error during calculation assets change percent"
            ) from e
