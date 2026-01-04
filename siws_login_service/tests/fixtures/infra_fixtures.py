"""Fixtures for infrastructure layer tests."""

from datetime import datetime, UTC

import pytest

from src.infrastructures.database.models.wallet_model import Wallet, WalletSession
from src.infrastructures.database.mappers.wallet_mapper import WalletDBMapper
from src.infrastructures.database.mappers.wallet_session_mapper import WalletSessionDBMapper
from src.infrastructures.database.mappers.nonce_mapper import NonceDBMapper
from src.infrastructures.database.models.nonce_model import Nonce


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
        wallet_address=sample_wallet_vo.value,
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


@pytest.fixture
def sample_db_wallet_session_model(sample_wallet_vo):
    """Fixture providing a sample WalletSession database model instance.

    Args:
        sample_wallet_vo: Fixture providing a valid WalletAddressVO instance.

    Returns:
        A WalletSession SQLAlchemy model instance with test data.
    """
    now = datetime.now(UTC)
    return WalletSession(
        wallet_address=sample_wallet_vo.value,
        device_id=123456789,
        refresh_token_hash="test_refresh_token_hash_12345",
        is_revoked=False,
        created_at=now,
    )


@pytest.fixture
def wallet_session_db_model(sample_wallet_session_vo):
    """Fixture providing WalletSessionVO converted to WalletSession database model.

    Args:
        sample_wallet_session_vo: Fixture providing a valid WalletSessionVO instance.

    Returns:
        A WalletSession SQLAlchemy model instance converted from WalletSessionVO.
    """
    return WalletSessionDBMapper.to_database_model(sample_wallet_session_vo)


@pytest.fixture
def wallet_session_mapper_from_db_model(sample_db_wallet_session_model):
    """Fixture providing WalletSession database model converted to WalletSessionVO.

    Args:
        sample_db_wallet_session_model: Fixture providing a valid WalletSession database model instance.

    Returns:
        A WalletSessionVO domain entity converted from WalletSession database model.
    """
    return WalletSessionDBMapper.from_database_model(sample_db_wallet_session_model)