from unittest.mock import AsyncMock

import pytest

from src.application.use_cases.send_request_use_case import SendRequestUseCase
from src.infrastructures.database.repositories.nonce_repository import SQLAlchemyNonceRepository
from src.application.use_cases.verify_signature_use_case import VerifySignatureUseCase
from src.infrastructures.crypto.ed25519_verifier import SignatureVerifier


@pytest.fixture
def mock_request_signature(fake_nonce_repository, fake_wallet_repository):
    return SendRequestUseCase(
        nonce_repository=fake_nonce_repository,
        wallet_repository=fake_wallet_repository,
    )

@pytest.fixture
def asyncmock_signature_verifier():
    verifier = AsyncMock(spec=SignatureVerifier)
    verifier.verify_signature = AsyncMock()
    return verifier

@pytest.fixture
def asyncmock_verify_signature_uc(fake_nonce_repository, asyncmock_signature_verifier):
    return VerifySignatureUseCase(
        nonce_repository=fake_nonce_repository,
        signature_verifier=asyncmock_signature_verifier,
    )


@pytest.fixture
def mock_verify_signature_uc(fake_nonce_repository, mock_signature_verifier):
    return VerifySignatureUseCase(
        nonce_repository=fake_nonce_repository,
        signature_verifier=AsyncMock(spec=SignatureVerifier),
    )

@pytest.fixture
def mock_nonce_repo():
    repo = AsyncMock(spec=SQLAlchemyNonceRepository)
    repo.create_nonce = AsyncMock()
    repo.find_active_nonce_by_wallet = AsyncMock()
    return repo

@pytest.fixture
def mock_request_signature_with_mock_repo(mock_nonce_repo, fake_wallet_repository):
    return SendRequestUseCase(
        nonce_repository=mock_nonce_repo,
        wallet_repository=fake_wallet_repository,
    )