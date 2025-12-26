from datetime import datetime, UTC, timedelta

import pytest
from domain.entities.nonce_entity import NonceEntity

from domain.exceptions import NonceAlreadyUsedError, DateValidationError


class TestNonceEntity:
    def test_create_valid_nonce_entity(
        self,
        sample_nonce_entity: NonceEntity,
    ):
        assert sample_nonce_entity.uuid is not None
        assert sample_nonce_entity.uri == "https://cryptoalrt.io/login/solana"
        assert sample_nonce_entity.version == "1"
        assert sample_nonce_entity.domain == "cryptoalrt.io"
        assert sample_nonce_entity.statement == "Statement is not empty."

    def test_mark_used_works_correct(
        self,
        sample_nonce_entity: NonceEntity,
    ):
        marked_as_used = sample_nonce_entity.mark_as_used()

        assert marked_as_used.used_at is not None

    def test_not_marks_as_used_again(
        self,
        sample_nonce_entity: NonceEntity,
    ):
        marked_as_used = sample_nonce_entity.mark_as_used()

        with pytest.raises(NonceAlreadyUsedError):
            marked_as_used.mark_as_used()

    def test_is_expired_works_correct(self, sample_nonce_entity_with_custom_datetime):
        time_in_past = datetime.now(UTC) - timedelta(days=3)

        with pytest.raises(DateValidationError):
            sample_nonce_entity_with_custom_datetime(
                issued_at=datetime.now(UTC),
                expiration_time=time_in_past,
            )