from decimal import Decimal

from application.interfaces.repositories import PortfolioRepositoryProtocol
from domain.entities.portfolio_entity import PortfolioEntity


class FakePortfolioRepository(PortfolioRepositoryProtocol):
    """Fake portfolio repository for testing purposes."""

    def __init__(self, portfolios: list[PortfolioEntity] | None = None):
        """Initialize fake repository with optional list of portfolios.

        Args:
            portfolios: Initial list of portfolios to store. Defaults to empty list.
        """
        self._portfolios: dict[str, PortfolioEntity] = {}
        if portfolios:
            for portfolio in portfolios:
                self._portfolios[portfolio.wallet_address] = portfolio

    async def get_portfolio_with_assets_and_prices(
        self, wallet_address: str
    ) -> PortfolioEntity | None:

        return self._portfolios.get(wallet_address)

    async def get_portfolio_total_value(
        self, wallet_address: str
    ) -> tuple[PortfolioEntity, Decimal] | None:
        portfolio = self._portfolios.get(wallet_address)
        if portfolio is None:
            return None

        total_value = portfolio.total_value if portfolio.total_value is not None else Decimal("0")
        return portfolio, total_value

    async def get_portfolio_with_assets_count(
        self, wallet_address: str
    ) -> tuple[PortfolioEntity, int] | None:
        """Retrieve portfolio with count of associated assets."""

        portfolio = self._portfolios.get(wallet_address)
        if portfolio is None:
            return None

        assets_count = (
            portfolio.assets_count
            if portfolio.assets_count is not None
            else (len(portfolio.assets) if portfolio.assets else 0)
        )
        return portfolio, assets_count

    async def save_portfolio(self, portfolio_entity: PortfolioEntity) -> PortfolioEntity:
        """Save a new portfolio entity."""
        self._portfolios[portfolio_entity.wallet_address] = portfolio_entity
        return portfolio_entity

    async def update_portfolio(self, portfolio_entity: PortfolioEntity) -> PortfolioEntity:
        """Update an existing portfolio entity."""
        if portfolio_entity.wallet_address not in self._portfolios:
            raise ValueError(
                f"Portfolio with wallet address {portfolio_entity.wallet_address} not found"
            )
        self._portfolios[portfolio_entity.wallet_address] = portfolio_entity
        return portfolio_entity
