"""Tests for WalletEntity domain entity."""

from dataclasses import FrozenInstanceError
from datetime import datetime, UTC, timedelta

import pytest
from freezegun import freeze_time

from src.domain.entities.wallet_entity import WalletEntity
from src.domain.exceptions import DateValidationError, InvalidWalletAddressError


class TestWalletEntity:
    """Test suite for WalletEntity domain entity."""

    def test_create_valid_wallet_entity(
        self,
        sample_wallet_entity: WalletEntity,
    ) -> None:
        """Test that a valid WalletEntity can be created from fixture.

        Args:
            sample_wallet_entity: Fixture providing a valid WalletEntity instance.
        """
        assert sample_wallet_entity is not None
        assert sample_wallet_entity.uuid is not None

    @freeze_time("2030-01-01 08:00:00")
    def test_ping_works_correct(
        self,
        sample_wallet_entity: WalletEntity,
    ) -> None:
        """Test that ping() method updates last_active timestamp.

        Uses 2030 because timestamp cannot be in the future, else test can break.

        Args:
            sample_wallet_entity: Fixture providing a valid WalletEntity instance.
        """
        pinged_wallet = sample_wallet_entity.ping()

        assert pinged_wallet.last_active > sample_wallet_entity.last_active

    @freeze_time("2030-01-01 08:00:00")
    def test_ping_returns_a_new_instance(
        self,
        sample_wallet_entity: WalletEntity,
    ) -> None:
        """Test that WalletEntity is immutable and ping() returns a new instance.

        Args:
            sample_wallet_entity: Fixture providing a valid WalletEntity instance.
        """
        with pytest.raises(FrozenInstanceError):
            sample_wallet_entity.last_active = "2030-01-01 08:00:00"

    @freeze_time("2030-01-01 08:00:00")
    def test_ping_saves_fields_correct(
        self,
        sample_wallet_entity: WalletEntity,
    ) -> None:
        """Test that ping() preserves other fields when updating last_active.

        Args:
            sample_wallet_entity: Fixture providing a valid WalletEntity instance.
        """
        pinged_wallet = sample_wallet_entity.ping()

        assert pinged_wallet.wallet_address.value == "5cRypRAdKEUtMCyFdqtEifWER5GMCfVnhZ8EUtcB7Sc3"

    def test_wallet_entity_convert_to_bytes_correct(
        self,
        sample_wallet_entity: WalletEntity,
    ) -> None:
        """Test that to_bytes() method returns correct byte representation.

        Args:
            sample_wallet_entity: Fixture providing a valid WalletEntity instance.
        """
        bytes_wallet = sample_wallet_entity.to_bytes()

        assert isinstance(bytes_wallet, bytes)
        assert len(bytes_wallet) == 32

    @freeze_time("2030-01-01 08:00:00")
    def test_wallet_entity_raises_date_validation_error(
        self,
        custom_wallet_entity: WalletEntity,
    ) -> None:
        """Test that DateValidationError is raised when created_at is in the future.

        Args:
            custom_wallet_entity: Fixture factory for creating WalletEntity
                                 with custom datetime values.
        """
        with pytest.raises(DateValidationError):
            custom_wallet_entity(
                created_at=datetime.now(UTC) + timedelta(days=2),
            )

    @pytest.mark.parametrize(
        "invalid_wallet",
        [
            "shortstring",
            "222",
            "23232",
            "longstring" * 20,
        ],
    )
    def test_incorrect_wallet_address_vo(
        self,
        invalid_wallet: str,
    ) -> None:
        """Test that InvalidWalletAddressError is raised for invalid wallet address.

        Args:
            invalid_wallet: Invalid wallet address string (wrong length or format).
        """
        with pytest.raises(InvalidWalletAddressError):
            WalletEntity.create(wallet_address=invalid_wallet)
