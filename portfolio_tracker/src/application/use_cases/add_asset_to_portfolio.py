from datetime import datetime, UTC
from decimal import Decimal

import structlog

from application.exceptions import UseCaseError
from application.interfaces import PortfolioRepositoryProtocol
from domain.entities.asset_entity import AssetEntity
from domain.exceptions import PortfolioNotFound, RepositoryError
from infrastructures.exceptions import DatabaseSavingError

logger = structlog.getLogger(__name__)


class AddAssetToPortfolioUseCase:
    def __init__(self, repository: PortfolioRepositoryProtocol):
        self._repository = repository

    async def execute(self, ticker: str, amount: Decimal, wallet_address: str) -> AssetEntity:
        try:
            portfolio = await self._repository.get_portfolio_by_wallet_address(
                wallet_address=wallet_address
            )

            if portfolio is None:
                logger.error(
                    "Portfolio not found during adding asset", wallet_address=wallet_address
                )
                raise PortfolioNotFound

            asset = AssetEntity.create(ticker=ticker, amount=amount, wallet_address=wallet_address)
            added_asset = await self._repository.add_asset(asset)

            # todo: need to add "AssetCreatedEvent" and publish it to broker

            return added_asset
        except (DatabaseSavingError, PortfolioNotFound, RepositoryError) as e:
            logger.error(
                "Operation failed",
                error_type=type(e).__name__,
                error=str(e),
                timestamp=datetime.now(UTC),
            )
            raise UseCaseError("Occurred error during adding asset to portfolio") from e

        except Exception as e:
            logger.error(
                "Operation failed",
                error_type=type(e).__name__,
                error=str(e),
                timestamp=datetime.now(UTC),
            )
            raise UseCaseError(
                "Occurred unexpected error during adding asset to portfolio"
            ) from e
