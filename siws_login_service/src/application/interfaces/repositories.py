from typing import Protocol

from domain.entities.wallet_entity import WalletEntity


class WalletRepositoryProtocol(Protocol):
    """Protocol for a wallet repository.

    Defines methods for retrieving, creating, and updating wallet entities.
    """

    async def get_wallet_by_address(
        self,
        wallet_address: str,
    ) -> WalletEntity | None:
        """Retrieve a wallet entity by its address.

        Args:
            wallet_address: The wallet address to search for.

        Returns:
            WalletEntity if found, None otherwise.
        """
        ...

    async def create_wallet(
        self,
        wallet_entity: WalletEntity,
    ) -> WalletEntity:
        """Create a new wallet entity in the database.

        Args:
            wallet_entity: The wallet entity to create.

        Returns:
            The created wallet entity.
        """
        ...

    async def update_values(
        self,
        wallet_address: str,
        wallet_entity: WalletEntity,
    ) -> WalletEntity:
        """Update wallet entity values in the database.

        Args:
            wallet_address: The wallet address to update.
            wallet_entity: The wallet entity with updated values.

        Returns:
            The updated wallet entity.
        """
        ...
