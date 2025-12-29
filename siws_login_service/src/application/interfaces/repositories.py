from typing import Protocol

from src.domain.entities.wallet_entity import WalletEntity
from src.domain.entities.nonce_entity import NonceEntity


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


class NonceRepositoryProtocol(Protocol):
    """Protocol for a nonce repository.

    Defines methods for retrieving, creating, and updating nonce entities.
    """

    async def find_active_nonce_by_wallet(
        self,
        wallet_address: str,
    ) -> NonceEntity | None:
        """Retrieve an active nonce entity by wallet address.

        An active nonce is one that:
        - Has not been used (used_at is None)
        - Has not expired (expiration_time > current time)

        Args:
            wallet_address: The wallet address to search for.

        Returns:
            NonceEntity if an active nonce is found, None otherwise.
        """
        ...

    async def find_nonce_by_wallet(
        self,
        wallet_address: str,
    ) -> NonceEntity | None:
        """Retrieve a nonce entity by wallet address.

        Args:
            wallet_address: The wallet address to search for.

        Returns:
            NonceEntity if found, None otherwise.
        """
        ...

    async def create_nonce(
        self,
        nonce_entity: NonceEntity,
    ) -> NonceEntity:
        """Create a new nonce entity in the database.

        Args:
            nonce_entity: The nonce entity to create.

        Returns:
            The created nonce entity.
        """
        ...

    async def update_nonce(
        self,
        nonce_uuid: str,
        nonce_entity: NonceEntity,
    ) -> NonceEntity:
        """Update nonce entity values in the database.

        Args:
            nonce_uuid: The nonce UUID to update.
            nonce_entity: The nonce entity with updated values.

        Returns:
            The updated nonce entity.
        """
        ...
