"""Mapper for converting between AssetEntity and Asset database model."""

from datetime import UTC

from domain.entities.asset_entity import AssetEntity
from infrastructures.database.models.asset import Asset


class AssetDBMapper:
    """Mapper for converting between AssetEntity and Asset database model."""

    @staticmethod
    def to_database(asset: AssetEntity) -> Asset:
        created_at = asset.created_at
        if created_at.tzinfo is not None:
            created_at = created_at.replace(tzinfo=None)

        return Asset(
            asset_id=asset.asset_id,
            ticker=asset.ticker,
            amount=asset.amount,
            wallet_address=asset.wallet_address,
            created_at=created_at,
        )

    @staticmethod
    def from_database(model: Asset) -> AssetEntity:
        """Convert Asset database model to AssetEntity.
        """
        created_at = model.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)

        return AssetEntity(
            asset_id=model.asset_id,
            ticker=model.ticker,
            amount=model.amount,
            wallet_address=model.wallet_address,
            created_at=created_at,
        )

    @staticmethod
    def to_dict(asset: AssetEntity) -> dict:
        """Convert AssetEntity to dict.
        """
        return {
            "asset_id": str(asset.asset_id),
            "ticker": asset.ticker,
            "amount": str(asset.amount),
            "wallet_address": asset.wallet_address,
            "created_at": asset.created_at.isoformat(),
        }