from datetime import datetime, UTC, timedelta
from os import access

import pytest

from src.domain.entities.nonce_entity import NonceEntity
from src.domain.value_objects.wallet_vo import WalletAddressVO
from src.domain.value_objects.nonce_vo import NonceVO
from src.domain.entities.wallet_entity import WalletEntity
from src.domain.events.wallet_logged_in_event import WalletLoggedInEvent
from src.domain.value_objects.signature_vo import SignatureVO
from src.domain.value_objects.message_vo import MessageVO

from src.domain.value_objects.token_vo import TokenPairVO


@pytest.fixture
def sample_wallet_vo():
    return WalletAddressVO(
        value="5cRypRAdKEUtMCyFdqtEifWER5GMCfVnhZ8EUtcB7Sc3"
    )

@pytest.fixture
def sample_nonce_vo():
    return NonceVO.generate()

@pytest.fixture
def sample_signature_vo():
    string = "5cRypRAdKEUtMCyFdqtEifWER5GMCfVnhZ8EUtcB7Sc35cRypRAdKEUtMCyFdqtEifWER5GMCfVnhZ8EUtcB7Sc3"
    return SignatureVO.from_string(value=string)


@pytest.fixture
def sample_nonce_entity(sample_wallet_vo, sample_nonce_vo) -> NonceEntity:
    return NonceEntity.create(
        wallet_address=sample_wallet_vo,
        nonce=sample_nonce_vo,
        statement="Statement is not empty.",
    )

@pytest.fixture
def custom_wallet_entity(sample_uuid, sample_wallet_vo):
    def _create(
            last_active: datetime | None = None,
            created_at: datetime | None = None,
    ) -> WalletEntity:
        if last_active is None:
            last_active = datetime.now(UTC)
        if created_at is None:
            created_at = datetime.now(UTC)
        return WalletEntity(
            uuid=sample_uuid,
            wallet_address=sample_wallet_vo,
            hashed_refresh="test_refresh_token_hash",
            is_revoked=False,
            created_at=created_at,
            last_active=last_active,
        )
    return _create


@pytest.fixture
def sample_nonce_entity_with_custom_datetime(sample_uuid, sample_wallet_vo, sample_nonce_vo):
    def _create(
        expiration_time: datetime | None = None,
        used_at: datetime | None = None,
        issued_at: datetime | None = None,
    ) -> NonceEntity:
        if issued_at is None:
            issued_at = datetime.now(UTC)
        if expiration_time is None:
            expiration_time = issued_at + timedelta(minutes=5)
        
        return NonceEntity(
            uuid=sample_uuid,
            wallet_address=sample_wallet_vo,
            nonce=sample_nonce_vo,
            domain="cryptoalrt.io",
            statement="Test statement",
            uri="https://cryptoalrt.io/login/solana",
            version="1",
            expiration_time=expiration_time,
            used_at=used_at,
            issued_at=issued_at,
        )
    
    return _create

@pytest.fixture
def sample_wallet_entity(sample_wallet_vo):
    return WalletEntity.create(
        wallet_address=sample_wallet_vo,
    )

@pytest.fixture
def sample_message_vo(sample_nonce_entity):
    return MessageVO.from_record(record=sample_nonce_entity)

@pytest.fixture
def sample_wallet_logged_in_event(sample_wallet_vo):
    return WalletLoggedInEvent.create_event(
        pubkey=sample_wallet_vo.value,
        device_id=999,
    )

@pytest.fixture
def sample_token_vo():
    return TokenPairVO.from_string(
        access_token="access.token.test",
        refresh_token="refresh.token.test",
    )