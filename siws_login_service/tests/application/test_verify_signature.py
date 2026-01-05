from typing import Any

import pytest

from src.application.use_cases.verify_signature_use_case import VerifySignatureUseCase
from src.domain.entities.nonce_entity import NonceEntity
from src.domain.exceptions import (
    NonceNotFoundError,
    SignatureVerificationFailed,
    NonceAlreadyUsedError,
)
from src.domain.value_objects.signature_vo import SignatureVO
from src.infrastructures.exceptions import (
    FailedToUpdateNonceError,
    InfrastructureError,
)

from src.domain.value_objects.token_vo import TokenPairVO


class TestVerifySignature:
    """Tests for VerifySignatureUseCase."""

    @pytest.mark.asyncio
    async def test_signature_verified_successfully(
        self,
        sample_nonce_entity: NonceEntity,
        mock_verify_signature_uc: VerifySignatureUseCase,
        fake_nonce_repository: "FakeNonceRepository",
    ) -> None:
        """Test successful signature verification."""
        created_nonce = await fake_nonce_repository.create_nonce(sample_nonce_entity)
        result = await mock_verify_signature_uc.execute(
            signature="signature",
            wallet_address=created_nonce.wallet_address.value,
        )

        assert result is not None
        assert isinstance(result, TokenPairVO)

    @pytest.mark.asyncio
    async def test_no_active_nonce_raises(
        self,
        sample_nonce_entity: NonceEntity,
        mock_verify_signature_uc: VerifySignatureUseCase,
    ) -> None:
        """Test error when no active nonce found."""
        with pytest.raises(NonceNotFoundError):
            await mock_verify_signature_uc.execute(
                signature="signature",
                wallet_address=sample_nonce_entity.wallet_address.value,
            )

    @pytest.mark.asyncio
    async def test_invalid_signature_raises(
        self,
        fake_nonce_repository: "FakeNonceRepository",
        asyncmock_signature_verifier: Any,
        asyncmock_verify_signature_uc: VerifySignatureUseCase,
        sample_signature_vo: SignatureVO,
        sample_nonce_entity: NonceEntity,
    ) -> None:
        """Test error when signature verification fails."""
        created_nonce = await fake_nonce_repository.create_nonce(sample_nonce_entity)
        asyncmock_signature_verifier.verify_signature.side_effect = SignatureVerificationFailed

        with pytest.raises(SignatureVerificationFailed):
            await asyncmock_verify_signature_uc.execute(
                signature=sample_signature_vo.value,
                wallet_address=created_nonce.wallet_address.value,
            )

    @pytest.mark.parametrize(
        "exception_, expected_exception",
        [
            (NonceNotFoundError, NonceNotFoundError),
            (SignatureVerificationFailed, SignatureVerificationFailed),
            (NonceAlreadyUsedError, NonceAlreadyUsedError),
            (FailedToUpdateNonceError, FailedToUpdateNonceError),
            (InfrastructureError, InfrastructureError),
            (Exception, InfrastructureError),
        ],
    )
    @pytest.mark.asyncio
    async def test_raises_on_error(
        self,
        exception_: type[Exception],
        expected_exception: type[Exception],
        fake_nonce_repository: "FakeNonceRepository",
        asyncmock_signature_verifier: Any,
        asyncmock_verify_signature_uc: VerifySignatureUseCase,
        sample_signature_vo: SignatureVO,
        sample_nonce_entity: NonceEntity,
    ) -> None:
        """Test error handling during signature verification."""
        created_nonce = await fake_nonce_repository.create_nonce(sample_nonce_entity)
        asyncmock_signature_verifier.verify_signature.side_effect = exception_

        with pytest.raises(expected_exception):
            await asyncmock_verify_signature_uc.execute(
                signature=sample_signature_vo.value,
                wallet_address=created_nonce.wallet_address.value,
            )

