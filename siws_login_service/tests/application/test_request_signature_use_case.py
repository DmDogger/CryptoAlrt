from typing import Any

import pytest

from src.domain.entities.nonce_entity import NonceEntity
from src.domain.value_objects.wallet_vo import WalletAddressVO
from src.infrastructures.exceptions import (
    InfrastructureError,
    FailedToSaveNonceError,
)
from tests.helpers.fakes import FakeNonceRepository
from src.application.use_cases.send_request_use_case import SendRequestUseCase


class TestRequestSignatureUseCase:
    """Tests for SendRequestUseCase."""

    @pytest.mark.asyncio
    async def test_no_nonce_creates_new(
        self,
        mock_request_signature: SendRequestUseCase,
        sample_wallet_vo: WalletAddressVO,
    ) -> None:
        """Test creating message when no active nonce exists."""
        result = await mock_request_signature.execute(wallet_address=sample_wallet_vo.value)

        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_existing_nonce_reused(
        self,
        fake_nonce_repository: FakeNonceRepository,
        mock_request_signature: SendRequestUseCase,
        sample_nonce_entity: NonceEntity,
    ) -> None:
        """Test reusing existing active nonce."""
        nonce = await fake_nonce_repository.create_nonce(sample_nonce_entity)
        result = await mock_request_signature.execute(wallet_address=nonce.wallet_address.value)

        assert isinstance(result, str)
        assert "cryptoalrt.io wants you to sign in with your Solana account" in result
        assert result is not None

    @pytest.mark.parametrize(
        "exception_, expected_exception",
        [
            (InfrastructureError, InfrastructureError),
            (FailedToSaveNonceError, FailedToSaveNonceError),
            (Exception, InfrastructureError),
        ],
    )
    @pytest.mark.asyncio
    async def test_raises_on_error(
        self,
        exception_: type[Exception],
        expected_exception: type[Exception],
        mock_nonce_repo: Any,
        mock_request_signature_with_mock_repo: SendRequestUseCase,
        sample_nonce_entity: NonceEntity,
    ) -> None:
        """Test error handling during nonce retrieval."""
        mock_nonce_repo.find_active_nonce_by_wallet.side_effect = exception_

        with pytest.raises(expected_exception):
            await mock_request_signature_with_mock_repo.execute(
                wallet_address=sample_nonce_entity.wallet_address.value
            )
