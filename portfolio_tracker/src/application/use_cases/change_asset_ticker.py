from datetime import datetime, UTC

import structlog
from application.exceptions import AssetNotExist, AssetUpdatingError, UseCaseError
from application.interfaces import PortfolioRepositoryProtocol
from domain.entities.asset_entity import AssetEntity
from domain.exceptions import PortfolioNotFound, RepositoryError
from infrastructures.exceptions import DatabaseSavingError

logger = structlog.getLogger(__name__)


class ChangeAssetTickerUseCase:
    """Use case for changing asset ticker in portfolio."""

    def __init__(self, repository: PortfolioRepositoryProtocol):
        self._repository = repository

    async def execute(self, wallet_address: str, old_ticker: str, new_ticker: str) -> AssetEntity:
        """Change asset ticker in portfolio.

        Args:
            wallet_address: Wallet address to find portfolio.
            old_ticker: Current cryptocurrency ticker symbol.
            new_ticker: New ticker symbol for the asset.

        Returns:
            Updated AssetEntity with new ticker.

        Raises:
            UseCaseError: If operation fails or data is invalid.
        """
        try:
            portfolio = await self._repository.get_portfolio_by_wallet_address(
                wallet_address=wallet_address
            )

            if portfolio is None:
                logger.error(
                    "Portfolio not found during changing asset ticker",
                    wallet_address=wallet_address,
                )
                raise PortfolioNotFound(f"Portfolio with wallet address {wallet_address} not found")

            existing_asset = await self._repository.get_asset_by_ticker(
                ticker=old_ticker, wallet_address=wallet_address
            )

            if existing_asset is None:
                logger.error(
                    "Asset not found during changing ticker",
                    ticker=old_ticker,
                    wallet_address=wallet_address,
                )
                raise AssetNotExist(
                    f"Asset with ticker {old_ticker} not found in portfolio {wallet_address}"
                )

            asset_to_upd = existing_asset.change_ticker(ticker=new_ticker)

            updated = await self._repository.update_asset(asset_to_upd)

            if updated is None:
                logger.error(
                    "Asset update returned None",
                    old_ticker=old_ticker,
                    new_ticker=new_ticker,
                    wallet_address=wallet_address,
                )
                raise AssetUpdatingError(
                    f"Failed to update asset {old_ticker} to {new_ticker} in portfolio {wallet_address}"
                )

            return updated

        except (
            AssetNotExist,
            AssetUpdatingError,
            DatabaseSavingError,
            PortfolioNotFound,
            RepositoryError,
        ) as e:
            logger.error(
                "Operation failed",
                error_type=type(e).__name__,
                error=str(e),
                timestamp=datetime.now(UTC),
            )
            raise UseCaseError("Occurred error during changing asset ticker") from e

        except Exception as e:
            logger.error(
                "Operation failed",
                error_type=type(e).__name__,
                error=str(e),
                timestamp=datetime.now(UTC),
            )
            raise UseCaseError("Occurred unexpected error during changing asset ticker") from e
