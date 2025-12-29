from unittest.mock import AsyncMock

import pytest

from application.use_cases.send_request_use_case import SendRequestUseCase

from infrastructures.database.repositories.nonce_repository import SQLAlchemyNonceRepository


@pytest.fixture
def mock_request_signature(fake_nonce_repository):
    return SendRequestUseCase(
        nonce_repository=fake_nonce_repository,
    )

@pytest.fixture
def mock_nonce_repo():
    repo = AsyncMock(spec=SQLAlchemyNonceRepository)
    repo.create_nonce = AsyncMock()
    repo.find_active_nonce_by_wallet = AsyncMock()
    return repo

@pytest.fixture
def mock_request_signature_with_mock_repo(mock_nonce_repo):
    return SendRequestUseCase(
        nonce_repository=mock_nonce_repo,
    )