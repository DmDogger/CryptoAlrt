"""Mapper for converting between WalletEntity and Wallet database model."""

from dataclasses import dataclass
from typing import final

from domain.entities.wallet_entity import WalletEntity
from infrastructures.database.models.wallet_model import Wallet


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class WalletDBMapper:
    """Mapper for converting between domain WalletEntity and database Wallet model.

    This mapper provides bidirectional conversion between the domain entity
    and the SQLAlchemy database model, ensuring proper data transformation.
    """

    @staticmethod
    def to_database_model(entity: WalletEntity) -> Wallet:
        """Converts a WalletEntity domain entity to a Wallet database model.

        Args:
            entity: The WalletEntity domain entity to convert.

        Returns:
            A Wallet SQLAlchemy model instance with data from the entity.
        """
        return Wallet(
            uuid=entity.uuid,
            wallet_address=entity.wallet_address,
            last_active=entity.last_active,
            created_at=entity.created_at,
        )

    @staticmethod
    def from_database_model(wallet: Wallet) -> WalletEntity:
        """Converts a Wallet database model to a WalletEntity domain entity.

        Args:
            wallet: The Wallet SQLAlchemy model instance to convert.

        Returns:
            A WalletEntity domain entity with data from the database model.
        """
        return WalletEntity(
            uuid=wallet.uuid,
            wallet_address=wallet.wallet_address,
            last_active=wallet.last_active,
            created_at=wallet.created_at,
        )
