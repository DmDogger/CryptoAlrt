from datetime import datetime, UTC

import structlog
from application.exceptions import UseCaseError
from application.interfaces import PortfolioRepositoryProtocol
from domain.entities.asset_entity import AssetEntity
from domain.entities.portfolio_entity import PortfolioEntity
from infrastructures.exceptions import DatabaseSavingError

logger = structlog.getLogger(__name__)


class InitiatePortfolioUseCase:
    """Use case for initiating a portfolio."""

    def __init__(self, repository: PortfolioRepositoryProtocol):
        self._repository = repository

    async def execute(
        self,
        wallet_address: str,
        assets: list[AssetEntity] | None = None,
    ) -> PortfolioEntity:
        """Initiate portfolio for a wallet address.

        Args:
            wallet_address: Wallet address for the portfolio.
            assets: Optional list of assets to attach to the portfolio.

        Returns:
            Created PortfolioEntity.

        Raises:
            UseCaseError: If portfolio initialization fails.
        """
        try:
            if assets is None:
                empty_portfolio = PortfolioEntity.create(wallet_address=wallet_address)

                saved_portfolio = await self._repository.save_portfolio(empty_portfolio)
                return saved_portfolio

            not_empty_portfolio = PortfolioEntity.create(
                wallet_address=wallet_address, assets=assets
            )
            saved_non_empty = await self._repository.save_portfolio(not_empty_portfolio)
            return saved_non_empty

        except DatabaseSavingError as e:
            logger.error(
                "Operation failed",
                error_type=type(e).__name__,
                error=str(e),
                timestamp=datetime.now(UTC),
            )
            raise UseCaseError("Occurred error during portfolio initiation") from e

        except Exception as e:
            logger.error(
                "Operation failed",
                error_type=type(e).__name__,
                error=str(e),
                timestamp=datetime.now(UTC),
            )
            raise UseCaseError("Occurred unexpected error during portfolio initiation") from e
