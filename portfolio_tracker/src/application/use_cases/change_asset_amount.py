from datetime import datetime, UTC
from decimal import Decimal

import structlog
from application.exceptions import AssetNotExist, AssetUpdatingError, UseCaseError
from application.interfaces import PortfolioRepositoryProtocol
from domain.entities.asset_entity import AssetEntity
from domain.exceptions import PortfolioNotFound, RepositoryError
from infrastructures.exceptions import DatabaseSavingError

logger = structlog.getLogger(__name__)


class ChangeAssetAmountUseCase:
    """Use case for changing asset amount in portfolio."""

    def __init__(self, repository: PortfolioRepositoryProtocol):
        self._repository = repository

    async def execute(self, wallet_address: str, ticker: str, amount: Decimal) -> AssetEntity:
        """Change asset amount in portfolio.

        Args:
            wallet_address: Wallet address to find portfolio.
            ticker: Cryptocurrency ticker symbol.
            amount: New amount for the asset.

        Returns:
            Updated AssetEntity with new amount.

        Raises:
            UseCaseError: If operation fails or data is invalid.
        """
        try:
            portfolio = await self._repository.get_portfolio_by_wallet_address(
                wallet_address=wallet_address
            )

            if portfolio is None:
                logger.error(
                    "Portfolio not found during changing asset amount",
                    wallet_address=wallet_address,
                )
                raise PortfolioNotFound(f"Portfolio with wallet address {wallet_address} not found")

            existing_asset = await self._repository.get_asset_by_ticker(
                ticker=ticker, wallet_address=wallet_address
            )

            if existing_asset is None:
                logger.error(
                    "Asset not found during changing amount",
                    ticker=ticker,
                    wallet_address=wallet_address,
                )
                raise AssetNotExist(
                    f"Asset with ticker {ticker} not found in portfolio {wallet_address}"
                )

            asset_to_upd = existing_asset.set_amount(amount=amount)

            updated = await self._repository.update_asset(asset_to_upd)

            if updated is None:
                logger.error(
                    "Asset update returned None",
                    ticker=ticker,
                    wallet_address=wallet_address,
                )
                raise AssetUpdatingError(
                    f"Failed to update asset {ticker} in portfolio {wallet_address}"
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
            raise UseCaseError("Occurred error during changing asset amount") from e

        except Exception as e:
            logger.error(
                "Operation failed",
                error_type=type(e).__name__,
                error=str(e),
                timestamp=datetime.now(UTC),
            )
            raise UseCaseError("Occurred unexpected error during changing asset amount") from e
