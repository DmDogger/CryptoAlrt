"""Mapper for converting between PortfolioEntity and Portfolio database model."""

from datetime import UTC, datetime, tzinfo
from decimal import Decimal
from typing import Any

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

        if portfolio.assets:
            seen_ids = set()
            unique_assets = []
            for asset in portfolio.assets:
                if asset.asset_id not in seen_ids:
                    seen_ids.add(asset.asset_id)
                    unique_assets.append(asset)

            return Portfolio(
                wallet_address=portfolio.wallet_address,
                assets=[AssetDBMapper.to_database(asset) for asset in unique_assets],
                total_value=portfolio.total_value,
                weight=portfolio.weight,
                portfolio_total=portfolio.portfolio_total,
                assets_count=portfolio.assets_count,
                updated_at=updated_at,
            )
        return Portfolio(
            wallet_address=portfolio.wallet_address,
            total_value=portfolio.total_value,
            weight=portfolio.weight,
            portfolio_total=portfolio.portfolio_total,
            assets_count=portfolio.assets_count,
            updated_at=updated_at,
        )

    @staticmethod
    def from_database(model: Portfolio) -> PortfolioEntity:
        """Convert Portfolio database model to PortfolioEntity."""
        updated_at = model.updated_at
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=UTC)

        total_value = Decimal(str(model.total_value)) if model.total_value is not None else None
        weight = Decimal(str(model.weight)) if model.weight is not None else None
        portfolio_total = (
            Decimal(str(model.portfolio_total)) if model.portfolio_total is not None else None
        )

        return PortfolioEntity(
            wallet_address=model.wallet_address,
            assets=(
                [AssetDBMapper.from_database(asset) for asset in model.assets]
                if model.assets
                else None
            ),
            total_value=total_value,
            weight=weight,
            portfolio_total=portfolio_total,
            assets_count=model.assets_count,
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
            "updated_at": portfolio.updated_at.replace(tzinfo=None),
            "assets_count": (
                portfolio.assets_count
                if portfolio.assets_count is not None
                else (len(portfolio.assets) if portfolio.assets else 0)
            ),
        }

    @staticmethod
    def from_dict(data: dict) -> PortfolioEntity:
        """Convert dict to PortfolioEntity."""
        updated_at = (
            datetime.fromisoformat(data.get("updated_at")).replace(tzinfo=UTC)
            if data.get("updated_at")
            else datetime.now(UTC)
        )
        return PortfolioEntity(
            wallet_address=data.get("wallet_address"),
            assets=data.get("assets", None),
            total_value=Decimal(data.get("total_value")) if data.get("total_value") else None,
            weight=Decimal(data.get("weight")) if data.get("weight") else None,
            portfolio_total=(
                Decimal(data.get("portfolio_total")) if data.get("portfolio_total") else None
            ),
            assets_count=data.get("assets_count", None),
            updated_at=updated_at,
        )

    @staticmethod
    def to_decimal(value: Any) -> Decimal:
        return Decimal(value)
