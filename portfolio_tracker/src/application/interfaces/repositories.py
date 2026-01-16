"""Repository protocol interfaces."""

from abc import abstractmethod
from decimal import Decimal
from typing import Protocol

from domain.entities.portfolio_entity import PortfolioEntity


class PortfolioRepositoryProtocol(Protocol):
    """Protocol for a portfolio repository.

    Defines methods for retrieving portfolio entities with assets and prices.
    """

    @abstractmethod
    async def get_portfolio_with_assets_and_prices(
        self, wallet_address: str
    ) -> PortfolioEntity | None:
        """Retrieve portfolio with assets and their current prices.

        Args:
            wallet_address: Wallet address to find portfolio.

        Returns:
            PortfolioEntity with loaded assets and prices, or None if not found.
        """
        ...

    @abstractmethod
    async def get_portfolio_total_value(
        self, wallet_address: str
    ) -> tuple[PortfolioEntity, Decimal] | None:
        """Calculate and retrieve portfolio total value.

        Total value is calculated as sum of (asset.amount * crypto_price.price).

        Args:
            wallet_address: Wallet address to find portfolio.

        Returns:
            Tuple of (PortfolioEntity, total_value), or None if not found.
        """
        ...

    @abstractmethod
    async def get_portfolio_with_assets_count(
        self, wallet_address: str
    ) -> tuple[PortfolioEntity, int] | None:
        """Retrieve portfolio with count of associated assets.

        Args:
            wallet_address: Wallet address to find portfolio.

        Returns:
            Tuple of (PortfolioEntity, assets_count), or None if not found.
        """
        ...

    @abstractmethod
    async def get_portfolio_total_value_only(self, wallet_address: str) -> Decimal:
        """Calculate and retrieve only portfolio total value without portfolio entity.

        Total value is calculated as sum of (asset.amount * crypto_price.price).
        Returns Decimal("0") if no assets found or calculation result is None.

        Args:
            wallet_address: Wallet address to find portfolio.

        Returns:
            Total value as Decimal. Returns Decimal("0") if portfolio not found or has no assets.

        Raises:
            RepositoryError: If database operation fails.
        """
        ...
