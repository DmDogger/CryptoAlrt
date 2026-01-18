from decimal import Decimal

from application.interfaces.repositories import PortfolioRepositoryProtocol
from domain.entities.portfolio_entity import PortfolioEntity
from domain.value_objects.analytics_vo import AnalyticsValueObject


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

        # Storage for crypto prices and price history
        self._crypto_prices: dict[str, Decimal] = {}  # ticker -> current_price
        self._price_history: dict[str, Decimal] = {}  # ticker -> last_price

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

    async def get_portfolio_total_value_only(self, wallet_address: str) -> Decimal:
        """Calculate and retrieve only portfolio total value without portfolio entity."""
        portfolio = self._portfolios.get(wallet_address)
        if portfolio is None or portfolio.assets is None:
            return Decimal("0")

        # Calculate total value based on current prices (like real repository)
        total_value = Decimal("0")
        for asset in portfolio.assets:
            current_price = self._crypto_prices.get(asset.ticker)
            if current_price is not None:
                total_value += asset.amount * current_price

        return total_value if total_value > 0 else Decimal("0")

    async def get_last_total_value(self, wallet_address: str, hours: int = 24) -> Decimal | None:
        """Calculate portfolio total value using last/historical prices.

        Args:
            wallet_address: Wallet address to find portfolio.
            hours: Hours back to look for historical price. Default 24.

        Returns:
            Total value using last prices, or None if no data available.
        """
        portfolio = self._portfolios.get(wallet_address)
        if portfolio is None or portfolio.assets is None:
            return None

        last_total_value = Decimal("0")
        has_data = False

        # Sum all assets: amount * last_price
        for asset in portfolio.assets:
            last_price = self._price_history.get(asset.ticker)
            if last_price is not None:
                last_total_value += asset.amount * last_price
                has_data = True

        if not has_data:
            return None

        return last_total_value

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

    async def get_current_and_last_prices(
        self,
        ticker: str,
        hours: int = 24,
    ) -> tuple[Decimal, Decimal | None] | None:
        """Get current and last prices for a ticker."""
        current_price = self._crypto_prices.get(ticker)
        if current_price is None:
            return None

        last_price = self._price_history.get(ticker)
        return current_price, last_price

    def add_crypto_price(self, ticker: str, price: Decimal) -> None:
        """Add current crypto price for testing."""
        self._crypto_prices[ticker] = price

    def add_price_history(self, ticker: str, price: Decimal) -> None:
        """Add historical price for testing."""
        self._price_history[ticker] = price

    async def get_position_value(
        self, ticker: str, wallet_address: str
    ) -> AnalyticsValueObject | None:
        """Get position value for a specific ticker in a portfolio.

        Args:
            ticker: Cryptocurrency ticker symbol.
            wallet_address: Wallet address to find portfolio.

        Returns:
            AnalyticsValueObject with ticker and position_value, or None if not found.
        """
        portfolio = self._portfolios.get(wallet_address)
        if portfolio is None or portfolio.assets is None:
            return None

        # Find all assets with matching ticker and sum their amounts
        total_amount = Decimal("0")
        assets_with_ticker = []
        for a in portfolio.assets:
            if a.ticker == ticker:
                total_amount += a.amount
                assets_with_ticker.append(a)

        if not assets_with_ticker:
            return None

        # Get price for the ticker
        price = self._crypto_prices.get(ticker)
        if price is None:
            return None

        # Calculate position value: total_amount * price
        position_value = total_amount * price

        return AnalyticsValueObject(
            ticker=ticker,
            position_value=position_value,
            allocation=None,
            port_change=None,
            amount=total_amount,
            current_price=price,
        )
