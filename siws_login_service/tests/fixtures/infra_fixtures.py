"""Fixtures for infrastructure layer tests."""

from datetime import datetime, UTC

import pytest

from infrastructures.database.models.wallet_model import Wallet
from infrastructures.database.mappers.wallet_mapper import WalletDBMapper
from infrastructures.database.mappers.nonce_mapper import NonceDBMapper
from infrastructures.database.models.nonce_model import Nonce


@pytest.fixture
def sample_db_wallet_model(sample_wallet_vo, sample_uuid):
    """Fixture providing a sample Wallet database model instance.

    Args:
        sample_wallet_vo: Fixture providing a valid WalletAddressVO instance.
        sample_uuid: Fixture providing a UUID for the wallet.

    Returns:
        A Wallet SQLAlchemy model instance with test data.
    """
    now = datetime.now(UTC)
    return Wallet(
        uuid=sample_uuid,
        wallet_address=sample_wallet_vo,
        last_active=now,
        created_at=now,
    )

@pytest.fixture
def nonce_db_model(sample_nonce_entity):
    return NonceDBMapper.to_database_model(sample_nonce_entity)

@pytest.fixture
def nonce_custom_nonce_db_model(
        sample_uuid
):
    def _create(
        expiration_time: int | None = 5,
        used_at: datetime | None = None,
        issued_at: datetime | None = None,
        version: int | None = 1,
    ):
        return Nonce(
        domain="domain",
        statement="Solana statement test test",
        uri="uri",
        version=version,
        uuid=sample_uuid,
        wallet_address="Base58address",
        expiration_time=expiration_time,
        used_at=used_at,
        issued_at=issued_at,


    )
    return _create


@pytest.fixture
def wallet_db_model(sample_wallet_entity):
    """Fixture providing WalletEntity converted to Wallet database model.

    Args:
        sample_wallet_entity: Fixture providing a valid WalletEntity instance.

    Returns:
        A Wallet SQLAlchemy model instance converted from WalletEntity.
    """
    return WalletDBMapper.to_database_model(sample_wallet_entity)


@pytest.fixture
def wallet_mapper_from_db_model(sample_db_wallet_model):
    """Fixture providing Wallet database model converted to WalletEntity.

    Args:
        sample_db_wallet_model: Fixture providing a valid Wallet database model instance.

    Returns:
        A WalletEntity domain entity converted from Wallet database model.
    """
    return WalletDBMapper.from_database_model(sample_db_wallet_model)


@pytest.fixture
def sample_wallet_db_mapper():
    """Fixture providing WalletDBMapper class for testing.

    Returns:
        WalletDBMapper class.
    """
    return WalletDBMapper