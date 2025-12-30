from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructures.database.repositories.wallet_repository import SQLAlchemyWalletRepository
from src.infrastructures.database.mappers.wallet_mapper import WalletDBMapper
from src.infrastructures.database.repositories.nonce_repository import SQLAlchemyNonceRepository
from src.infrastructures.database.mappers.nonce_mapper import NonceDBMapper
from src.infrastructures.crypto.ed25519_verifier import SignatureVerifier

from tests.helpers.fakes import FakeNonceRepository, FakeWalletRepository


@pytest.fixture
def mock_wallet_mapper():
    mapper = MagicMock(spec=WalletDBMapper)
    mapper.to_database = MagicMock()
    mapper.from_database = MagicMock()
    return mapper

@pytest.fixture
def mock_nonce_mapper():
    mapper = MagicMock(spec=NonceDBMapper)
    mapper.to_database = MagicMock()
    mapper.from_database = MagicMock()
    return mapper

@pytest.fixture
def mock_result_obj():
    result = MagicMock(spec=ScalarResult)
    result.first = MagicMock()
    result.all = MagicMock()
    result.scalar_one_or_none = MagicMock()
    return result

@pytest.fixture
def mock_async_session() -> AsyncMock:
    """Мок AsyncSession для тестов репозиториев."""
    session = AsyncMock(spec=AsyncSession)
    session.scalars = AsyncMock()
    session.scalar_one = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.get = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    return session

@pytest.fixture
def fake_nonce_repository():
    return FakeNonceRepository()

@pytest.fixture
def fake_wallet_repository():
    return FakeWalletRepository()

@pytest.fixture
def mock_signature_verifier(fake_nonce_repository):
    return SignatureVerifier(_nonce_repository=fake_nonce_repository)

@pytest.fixture
def mock_wallet_repository(
    mock_async_session: AsyncMock,
    mock_wallet_mapper: MagicMock,
) -> SQLAlchemyWalletRepository:
    """Реальный SQLAlchemyWalletRepository с мок-сессией для тестов."""
    return SQLAlchemyWalletRepository(
        _session=mock_async_session,
        _mapper=mock_wallet_mapper,
    )

@pytest.fixture
def mock_nonce_repository(
        mock_async_session: AsyncMock,
        mock_nonce_mapper: MagicMock,
):
    return SQLAlchemyNonceRepository(
        _session=mock_async_session,
        _mapper=mock_nonce_mapper
    )