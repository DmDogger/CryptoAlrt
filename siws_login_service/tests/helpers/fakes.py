from datetime import datetime, UTC
from typing import Dict, Tuple
from uuid import UUID

from src.domain.entities.nonce_entity import NonceEntity
from src.domain.entities.wallet_entity import WalletEntity
from src.domain.value_objects.wallet_session_vo import WalletSessionVO
from src.infrastructures.exceptions import (
    FailedToSaveNonceError,
    FailedToUpdateNonceError,
    NonceNotFoundError,
    FailedToSaveWalletError,
    FailedToUpdateWalletError,
    WalletNotFoundError,
    SessionSaveFailed,
    RevokeSessionError,
)


class FakeNonceRepository:
    def __init__(self):
        self._by_wallet: Dict[str, NonceEntity] = {}
        self._by_uuid: Dict[UUID, NonceEntity] = {}

    async def find_active_nonce_by_wallet(
            self,
            wallet_address: str,
    ) -> NonceEntity | None:
        nonce = self._by_wallet.get(wallet_address)
        if nonce is None:
            return None

        if nonce.used_at is not None or nonce.is_expired():
            return None
        return nonce

    async def find_nonce_by_wallet(
            self,
            wallet_address: str,
    ) -> NonceEntity | None:
        return self._by_wallet.get(wallet_address)

    async def create_nonce(
            self,
            nonce_entity: NonceEntity,
    ) -> NonceEntity:
        wallet_address = nonce_entity.wallet_address.value
        if nonce_entity.uuid in self._by_uuid:
            raise FailedToSaveNonceError(
                f"Nonce with UUID {nonce_entity.uuid} already exists "
                f"or constraint violated"
            )
        self._by_wallet[wallet_address] = nonce_entity
        self._by_uuid[nonce_entity.uuid] = nonce_entity
        return nonce_entity

    async def update_nonce(
            self,
            nonce_uuid: str,
            nonce_entity: NonceEntity,
    ) -> NonceEntity:
        uuid_obj = UUID(nonce_uuid) if isinstance(nonce_uuid, str) else nonce_uuid
        if uuid_obj not in self._by_uuid:
            raise NonceNotFoundError(
                f"Cannot update nonce: nonce with UUID {nonce_uuid} not found"
            )
        wallet_address = nonce_entity.wallet_address.value
        self._by_wallet[wallet_address] = nonce_entity
        self._by_uuid[uuid_obj] = nonce_entity
        return nonce_entity


class FakeWalletRepository:
    def __init__(self):
        self._storage: Dict[str, WalletEntity] = {}
        self._sessions: Dict[Tuple[str, int], WalletSessionVO] = {}

    async def get_wallet_by_address(
            self,
            wallet_address: str,
    ) -> WalletEntity | None:
        return self._storage.get(wallet_address)

    async def create_wallet(
            self,
            wallet_entity: WalletEntity,
    ) -> WalletEntity:
        wallet_address = wallet_entity.wallet_address.value
        if wallet_address in self._storage:
            raise FailedToSaveWalletError(
                f"Wallet with address {wallet_address} "
                f"already exists or constraint violated"
            )
        self._storage[wallet_address] = wallet_entity
        return wallet_entity

    async def update_values(
            self,
            wallet_address: str,
            wallet_entity: WalletEntity,
    ) -> WalletEntity:
        if wallet_address not in self._storage:
            raise WalletNotFoundError(
                f"Cannot update wallet: wallet with address "
                f"{wallet_address} not found"
            )
        self._storage[wallet_address] = wallet_entity
        return wallet_entity

    async def save_session(
            self,
            wallet_vo: WalletSessionVO,
    ) -> WalletSessionVO:
        """Save a wallet session (fake implementation).

        Args:
            wallet_vo: The WalletSessionVO value object to save.

        Returns:
            The saved WalletSessionVO instance.

        Raises:
            SessionSaveFailed: If session already exists.
        """
        key = (wallet_vo.wallet_address.value, wallet_vo.device_id)
        if key in self._sessions:
            raise SessionSaveFailed(
                f"Failed to save wallet session: session with wallet address "
                f"{wallet_vo.wallet_address.value} and device_id {wallet_vo.device_id} "
                f"already exists or constraint violated"
            )
        self._sessions[key] = wallet_vo
        return wallet_vo

    async def get_sessions_by_wallet(
            self,
            wallet_address: str,
    ) -> list[WalletSessionVO]:
        """Retrieve all wallet sessions for a given wallet address (fake implementation).

        Args:
            wallet_address: The wallet address to search for sessions.

        Returns:
            List of WalletSessionVO instances for the specified wallet address.
            Returns empty list if no sessions are found.
        """
        sessions = [
            session
            for (addr, _), session in self._sessions.items()
            if addr == wallet_address
        ]
        return sessions

    async def revoke_single_session(
            self,
            wallet_address: str,
            device_id: int,
    ) -> WalletSessionVO:
        """Revoke a single wallet session by wallet address and device ID (fake implementation).

        Args:
            wallet_address: The wallet address of the session to revoke.
            device_id: The device ID of the session to revoke.

        Returns:
            The revoked WalletSessionVO instance.

        Raises:
            RevokeSessionError: If session is not found.
        """
        key = (wallet_address, device_id)
        if key not in self._sessions:
            raise RevokeSessionError(
                f"Failed to revoke wallet session: session with wallet address "
                f"{wallet_address} and device_id {device_id} not found"
            )
        session = self._sessions[key]
        revoked_session = session.revoke()
        self._sessions[key] = revoked_session
        return revoked_session

    async def terminate_all_sessions(
            self,
            wallet_address: str,
    ) -> list[WalletSessionVO]:
        """Terminate all wallet sessions for a given wallet address (fake implementation).

        Args:
            wallet_address: The wallet address for which to terminate all sessions.

        Returns:
            List of revoked WalletSessionVO instances.

        Raises:
            RevokeSessionError: If no sessions found.
        """
        revoked_sessions = []
        keys_to_update = []

        for (addr, device_id), session in self._sessions.items():
            if addr == wallet_address:
                keys_to_update.append((addr, device_id))
                revoked_session = session.revoke()
                revoked_sessions.append(revoked_session)

        if not revoked_sessions:
            raise RevokeSessionError(
                f"Failed to terminate all wallet sessions for wallet address "
                f"{wallet_address}: no active sessions found"
            )

        for i, key in enumerate(keys_to_update):
            self._sessions[key] = revoked_sessions[i]

        return revoked_sessions