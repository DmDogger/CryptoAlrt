from unittest.mock import AsyncMock

import pytest

from src.application.use_cases.send_request_use_case import SendRequestUseCase
from src.infrastructures.database.repositories.nonce_repository import SQLAlchemyNonceRepository
from src.application.use_cases.verify_signature_use_case import VerifySignatureUseCase
from src.infrastructures.crypto.ed25519_verifier import SignatureVerifier

from unittest.mock import AsyncMock, MagicMock

from src.application.use_cases.access_token_use_case import AccessTokenIssueUseCase
from src.application.use_cases.refresh_token_use_case import RefreshTokenIssueUseCase
from src.application.use_cases.tokens_issuer_use_case import TokensIssuerUseCase



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

@pytest.fixture
def mock_access_token_use_case(mock_access_issuer):
    """Fixture providing AccessTokenIssueUseCase with test issuer."""
    return AccessTokenIssueUseCase(access_issuer=mock_access_issuer)


@pytest.fixture
def mock_refresh_token_use_case(mock_refresh_issuer):
    """Fixture providing RefreshTokenIssueUseCase with test issuer."""
    return RefreshTokenIssueUseCase(refresh_issuer=mock_refresh_issuer)


@pytest.fixture
def mock_tokens_issuer_with_mocks(
    mock_refresh_token_use_case_mock,
    mock_access_token_use_case_mock,
):
    """Fixture providing TokensIssuerUseCase with mocked use cases for side effects."""
    return TokensIssuerUseCase(
        access_issuer_uc=mock_access_token_use_case_mock,
        refresh_issuer_uc=mock_refresh_token_use_case_mock,
    )


@pytest.fixture
def mock_access_token_use_case_mock():
    """Fixture providing mocked AccessTokenIssueUseCase for testing side effects."""
    mock = MagicMock(spec=AccessTokenIssueUseCase)
    mock.execute = MagicMock()
    return mock


@pytest.fixture
def mock_refresh_token_use_case_mock():
    """Fixture providing mocked RefreshTokenIssueUseCase for testing side effects."""
    mock = MagicMock(spec=RefreshTokenIssueUseCase)
    mock.execute = MagicMock()
    return mock



@pytest.fixture
def mock_tokens_issuer(
    mock_refresh_token_use_case,
    mock_access_token_use_case,
):
    """Fixture providing TokensIssuerUseCase with test dependencies."""
    return TokensIssuerUseCase(
        access_issuer_uc=mock_access_token_use_case,
        refresh_issuer_uc=mock_refresh_token_use_case,
    )