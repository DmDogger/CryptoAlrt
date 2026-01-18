from datetime import datetime, UTC

import structlog
from application.exceptions import TotalValueUnableToCalculate, UseCaseError
from application.interfaces import PortfolioRepositoryProtocol
from domain.exceptions import RepositoryError, DomainValidationError
from domain.services.analytics_service import AnalyticsService

logger = structlog.getLogger(__name__)


class RecalculatePortfolioChangeUseCase:
    def __init__(self, repository: PortfolioRepositoryProtocol):
        self._repository = repository

    async def execute(self, wallet_address: str):
        try:
            last_total_value = await self._repository.get_last_total_value(
                wallet_address=wallet_address
            )

            current_total_value = await self._repository.get_portfolio_total_value_only(
                wallet_address=wallet_address,
            )

            if last_total_value is None or current_total_value is None:
                raise TotalValueUnableToCalculate("Not found last or current total value")

            percent = AnalyticsService.portfolio_change(
                last_price=last_total_value,
                current_price=current_total_value,
            )
            return percent

        except (RepositoryError, DomainValidationError) as e:
            logger.error(
                "Operation failed",
                error_type=type(e).__name__,
                error=str(e),
                timestamp=datetime.now(UTC),
            )
            raise UseCaseError("Occurred error during recalculating portfolio's change") from e

        except Exception as e:
            logger.error(
                "Operation failed",
                error_type=type(e).__name__,
                error=str(e),
                timestamp=datetime.now(UTC),
            )
            raise UseCaseError(
                "Occurred unexpected error during recalculating portfolio's change"
            ) from e
