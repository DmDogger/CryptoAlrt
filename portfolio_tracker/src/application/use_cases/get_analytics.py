from datetime import datetime, UTC
from decimal import Decimal

import structlog
from application.exceptions import TotalValueUnableToCalculate, UseCaseError
from application.interfaces import PortfolioRepositoryProtocol
from application.use_cases.calculate_weight import CalculateWeightUseCase
from application.use_cases.recalculate_portfolio_change import RecalculatePortfolioChangeUseCase
from domain.value_objects.analytics_vo import AnalyticsValueObject
from domain.services.analytics_service import AnalyticsService
from application.use_cases.calculate_asset_change import CalculateAssetChangeUseCase
from domain.exceptions import RepositoryError, DomainValidationError, PortfolioNotFound

logger = structlog.getLogger(__name__)


class GetPortfolioAnalyticsUseCase:
    """Use case for retrieving portfolio analytics with calculated metrics."""

    def __init__(
        self,
        repository: PortfolioRepositoryProtocol,
        calculate_change: CalculateAssetChangeUseCase,
    ):
        """Initialize the use case with repository and change calculator.

        Args:
            repository: Repository for portfolio data access.
            calculate_change: Use case for calculating asset price changes.
        """
        self._repository = repository
        self._calculate_change = calculate_change

    async def execute(self, wallet_address: str) -> list[AnalyticsValueObject]:
        """Retrieve portfolio analytics with calculated allocation and price changes.

        Args:
            wallet_address: Wallet address to find portfolio.

        Returns:
            List of AnalyticsValueObject with position values, allocations,
            price changes, and other analytics metrics for each asset.

        Raises:
            UseCaseError: If portfolio not found, calculation fails, or data is invalid.
        """
        try:

            recalculated = []

            p = await self._repository.get_portfolio_by_wallet_address(
                wallet_address=wallet_address
            )

            if p is None:
                raise PortfolioNotFound

            analytics_objects = await self._repository.get_position_values(
                wallet_address=wallet_address
            )
            total_value = await self._repository.get_portfolio_total_value_only(
                wallet_address=wallet_address
            )

            if analytics_objects is None:
                return []

            if total_value is None:
                raise TotalValueUnableToCalculate

            for obj in analytics_objects:
                allocation = AnalyticsService.calculate_allocation(
                    asset_value=obj.position_value or Decimal("0"), total_value=total_value
                )

                port_change = await self._calculate_change.execute(ticker=obj.ticker)

                analytics_object = AnalyticsValueObject.create(
                    ticker=obj.ticker,
                    position_value=obj.position_value,
                    allocation=allocation,
                    port_change=port_change,
                    amount=obj.amount,
                    current_price=obj.current_price,
                    portfolio_weight=obj.portfolio_weight,
                    portfolio_change=obj.portfolio_change,
                )

                recalculated.append(analytics_object)
            return recalculated

        except (
            RepositoryError,
            TotalValueUnableToCalculate,
            DomainValidationError,
            PortfolioNotFound,
        ) as e:
            logger.error(
                "Operation failed",
                error_type=type(e).__name__,
                error=str(e),
                timestamp=datetime.now(UTC),
            )
            raise UseCaseError("Occurred error ") from e

        except Exception as e:
            logger.error(
                "Operation failed",
                error_type=type(e).__name__,
                error=str(e),
                timestamp=datetime.now(UTC),
            )
            raise UseCaseError("Occurred unexpected error") from e
