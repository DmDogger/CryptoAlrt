"""Mapper for converting between PortfolioEntity and Portfolio database model."""

from datetime import UTC

from domain.entities.portfolio_entity import PortfolioEntity
from infrastructures.database.models.portfolio import Portfolio

from infrastructures.database.mappers.asset_db_mapper import AssetDBMapper


class PortfolioDBMapper:
    """Mapper for converting between PortfolioEntity and Portfolio database model."""

    @staticmethod
    def to_database(portfolio: PortfolioEntity) -> Portfolio:
        """Convert PortfolioEntity to Portfolio database model."""
        updated_at = portfolio.updated_at
        if updated_at.tzinfo is not None:
            updated_at = updated_at.replace(tzinfo=None)

        return Portfolio(
            wallet_address=portfolio.wallet_address,
            total_value=portfolio.total_value,
            weight=portfolio.weight,
            portfolio_total=portfolio.portfolio_total,
            updated_at=updated_at,
        )

    @staticmethod
    def from_database(model: Portfolio) -> PortfolioEntity:
        """Convert Portfolio database model to PortfolioEntity."""
        updated_at = model.updated_at
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=UTC)

        return PortfolioEntity(
            wallet_address=model.wallet_address,
            assets=(
                [AssetDBMapper.from_database(asset) for asset in model.assets]
                if model.assets
                else None
            ),
            total_value=model.total_value,
            weight=model.weight,
            portfolio_total=model.portfolio_total,
            updated_at=updated_at,
        )

    @staticmethod
    def to_dict(portfolio: PortfolioEntity) -> dict:
        """Convert PortfolioEntity to dict."""
        return {
            "wallet_address": portfolio.wallet_address,
            "total_value": str(portfolio.total_value) if portfolio.total_value else None,
            "weight": str(portfolio.weight) if portfolio.weight else None,
            "portfolio_total": (
                str(portfolio.portfolio_total) if portfolio.portfolio_total else None
            ),
            "updated_at": portfolio.updated_at.isoformat(),
            "assets_count": len(portfolio.assets),
        }
