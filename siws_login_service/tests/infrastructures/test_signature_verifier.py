from datetime import datetime, UTC, timedelta
from uuid import uuid4

import base58
import pytest
from nacl.signing import SigningKey

from src.domain.entities.nonce_entity import NonceEntity
from src.domain.value_objects.message_vo import MessageVO
from src.domain.value_objects.wallet_vo import WalletAddressVO
from src.domain.value_objects.nonce_vo import NonceVO
from src.infrastructures.crypto.ed25519_verifier import SignatureVerifier
from tests.helpers.fakes import FakeNonceRepository


class TestSignatureVerifier:
    @pytest.mark.asyncio
    async def test_signature_verifier_works_correct(
        self,
        mock_signature_verifier: SignatureVerifier,
        fake_nonce_repository: FakeNonceRepository,
        sample_nonce_entity: NonceEntity,
    ) -> None:
        """Test verifies correct operation of Ed25519 signature verifier.

        The test creates a new signing key, generates a nonce entity, forms
        a SIWS message from the nonce, signs it, and verifies that the verifier
        successfully validates the signature.

        Args:
            mock_signature_verifier: SignatureVerifier instance for signature verification.
            fake_nonce_repository: Fake repository for storing nonces.
            sample_nonce_entity: Sample nonce entity (not used, a new one is created).
        """
        signing_key: SigningKey = SigningKey.generate()
        verify_key = signing_key.verify_key
        verify_key_bytes: bytes = verify_key.encode()

        verify_key_base58: str = base58.b58encode(verify_key_bytes).decode("utf-8")
        wallet_address_vo: WalletAddressVO = WalletAddressVO(value=verify_key_base58)

        nonce_entity: NonceEntity = NonceEntity(
            uuid=uuid4(),
            wallet_address=wallet_address_vo,
            nonce=NonceVO.generate(),
            domain="cryptoalrt.io",
            statement="Test statement",
            uri="https://cryptoalrt.io/login/solana",
            version="1",
            expiration_time=datetime.now(UTC) + timedelta(minutes=5),
            issued_at=datetime.now(UTC),
            chain_id="mainnet-beta",
        )

        message_vo: MessageVO = MessageVO.from_record(nonce_entity)
        message_string: str = message_vo.to_string()
        message_bytes: bytes = message_string.encode("utf-8")

        signed = signing_key.sign(message_bytes)
        signature_base58: str = base58.b58encode(signed.signature).decode("utf-8")

        await fake_nonce_repository.create_nonce(nonce_entity)

        result: bool = await mock_signature_verifier.verify_signature(
            wallet_address=verify_key_base58,
            signature=signature_base58,
        )

        assert result is True
