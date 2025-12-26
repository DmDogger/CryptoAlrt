"""Tests for NonceEntity domain entity."""

from datetime import datetime, UTC, timedelta
from uuid import uuid4

import pytest
from freezegun import freeze_time

from domain.entities.nonce_entity import NonceEntity
from domain.exceptions import NonceAlreadyUsedError, DateValidationError
from domain.value_objects.nonce_vo import NonceVO
from domain.value_objects.wallet_vo import WalletAddressVO


class TestNonceEntity:
    """Test suite for NonceEntity domain entity."""

    def test_create_valid_nonce_entity(
        self,
        sample_nonce_entity: NonceEntity,
    ) -> None:
        """Test that a valid NonceEntity can be created from fixture.
        
        Args:
            sample_nonce_entity: Fixture providing a valid NonceEntity instance.
        """
        assert sample_nonce_entity.uuid is not None
        assert sample_nonce_entity.uri == "https://cryptoalrt.io/login/solana"
        assert sample_nonce_entity.version == "1"
        assert sample_nonce_entity.domain == "cryptoalrt.io"
        assert sample_nonce_entity.statement == "Statement is not empty."

    def test_mark_used_works_correct(
        self,
        sample_nonce_entity: NonceEntity,
    ) -> None:
        """Test that mark_as_used() method sets used_at timestamp.
        
        Args:
            sample_nonce_entity: Fixture providing a valid NonceEntity instance.
        """
        marked_as_used = sample_nonce_entity.mark_as_used()

        assert marked_as_used.used_at is not None
        assert isinstance(marked_as_used.used_at, datetime)

    def test_not_marks_as_used_again(
        self,
        sample_nonce_entity: NonceEntity,
    ) -> None:
        """Test that mark_as_used() raises error when nonce is already used.
        
        Args:
            sample_nonce_entity: Fixture providing a valid NonceEntity instance.
        """
        marked_as_used = sample_nonce_entity.mark_as_used()

        with pytest.raises(NonceAlreadyUsedError):
            marked_as_used.mark_as_used()

    def test_datetime_validator_works_correct(
        self,
        sample_nonce_entity_with_custom_datetime,
    ) -> None:
        """Test that DateValidationError is raised when issued_at >= expiration_time.
        
        Args:
            sample_nonce_entity_with_custom_datetime: Fixture factory for creating NonceEntity
                                                      with custom datetime values.
        """
        time_in_past = datetime.now(UTC) - timedelta(days=3)

        with pytest.raises(DateValidationError):
            sample_nonce_entity_with_custom_datetime(
                issued_at=datetime.now(UTC),
                expiration_time=time_in_past,
            )

    @freeze_time("2025-05-26 08:00:00")
    def test_is_expired_works_correct(
        self,
        sample_nonce_vo: NonceVO,
        sample_wallet_vo: WalletAddressVO,
    ) -> None:
        """Test that is_expired() returns False for non-expired nonce.
        
        Args:
            sample_nonce_vo: Fixture providing a valid NonceVO instance.
            sample_wallet_vo: Fixture providing a valid WalletAddressVO instance.
        """
        nonce_entity = NonceEntity(
            uuid=uuid4(),
            wallet_address=sample_wallet_vo,
            nonce=sample_nonce_vo,
            domain="cryptoalrt.io",
            statement="Test statement",
            uri="https://cryptoalrt.io/login/solana",
            version="1",
            expiration_time=datetime.now(UTC) + timedelta(days=1),
            used_at=None,
            issued_at=datetime.now(UTC) - timedelta(days=1),
        )

        assert nonce_entity.is_expired() is False

    @freeze_time("2025-05-26 08:00:00")
    def test_is_used_works_correct(
        self,
        sample_wallet_vo: WalletAddressVO,
        sample_nonce_vo: NonceVO,
    ) -> None:
        """Test that is_used() returns True when nonce has been used.
        
        Args:
            sample_wallet_vo: Fixture providing a valid WalletAddressVO instance.
            sample_nonce_vo: Fixture providing a valid NonceVO instance.
        """
        nonce_entity = NonceEntity(
            uuid=uuid4(),
            wallet_address=sample_wallet_vo,
            nonce=sample_nonce_vo,
            domain="cryptoalrt.io",
            statement="Test statement",
            uri="https://cryptoalrt.io/login/solana",
            version="1",
            expiration_time=datetime.now(UTC) + timedelta(minutes=59),
            used_at=datetime.now(UTC) + timedelta(minutes=49),
            issued_at=datetime.now(UTC),
        )

        assert nonce_entity.is_used() is True