from datetime import datetime, UTC
from typing import Dict
from uuid import UUID

from domain.entities.nonce_entity import NonceEntity
from domain.entities.wallet_entity import WalletEntity
from infrastructures.exceptions import (
    FailedToSaveNonceError,
    FailedToUpdateNonceError,
    NonceNotFoundError,
    FailedToSaveWalletError,
    FailedToUpdateWalletError,
    WalletNotFoundError,
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