"""Tests for WalletAddressVO value object."""

from decimal import Decimal
from typing import Any

import pytest
from src.domain.value_objects.wallet_vo import WalletAddressVO
from src.domain.exceptions import InvalidWalletAddressError


class TestWalletAddressVO:
    """Test suite for WalletAddressVO value object."""

    def test_create_valid_wallet_address_vo(
        self,
        sample_wallet_vo: WalletAddressVO,
    ) -> None:
        """Test that a valid WalletAddressVO can be created from fixture.
        
        Args:
            sample_wallet_vo: Fixture providing a valid WalletAddressVO instance.
        """
        assert sample_wallet_vo.value is not None
        assert sample_wallet_vo.value == "5cRypRAdKEUtMCyFdqtEifWER5GMCfVnhZ8EUtcB7Sc3"

    def test_correct_wallet_to_bytes(
        self,
        sample_wallet_vo: WalletAddressVO,
    ) -> None:
        """Test that to_bytes() method returns correct byte representation.
        
        Args:
            sample_wallet_vo: Fixture providing a valid WalletAddressVO instance.
        """
        bytes_wallet = sample_wallet_vo.to_bytes()

        assert isinstance(bytes_wallet, bytes)
        assert len(bytes_wallet) == 32

    def test_correct_wallet_instance_from_string(
        self,
        sample_wallet_vo: WalletAddressVO,
    ) -> None:
        """Test that from_string() factory method creates valid WalletAddressVO instance.
        
        Args:
            sample_wallet_vo: Fixture providing a valid WalletAddressVO instance (unused but required).
        """
        correct_instance = WalletAddressVO.from_string("5cRypRAdKEUtMCyFdqtEifWER5GMCfVnhZ8EUtcB7Sc3")

        assert isinstance(correct_instance, WalletAddressVO)
        assert correct_instance.value == "5cRypRAdKEUtMCyFdqtEifWER5GMCfVnhZ8EUtcB7Sc3"

    @pytest.mark.parametrize(
        "invalid_string",
        [
            "tooshort",
            "too1ong" * 100,
        ],
    )
    def test_raises_error_from_string_method(
        self,
        invalid_string: str,
        sample_wallet_vo: WalletAddressVO,
    ) -> None:
        """Test that from_string() raises error for invalid wallet address length.
        
        Args:
            invalid_string: Invalid wallet address string (wrong length).
            sample_wallet_vo: Fixture providing a valid WalletAddressVO instance (unused but required).
        """
        with pytest.raises(InvalidWalletAddressError):
            WalletAddressVO.from_string(invalid_string)

    @pytest.mark.parametrize(
        "invalid_alphabet_letters",
        [
            "000000000",
            "OOOOOOOOO",
            "IIIIIIIII",
            "lllllllll",
            "*********",
            "//////////",
        ],
    )
    def test_raises_error_when_incorrect_alphabet_for_base58(
        self,
        invalid_alphabet_letters: str,
        sample_wallet_vo: WalletAddressVO,
    ) -> None:
        """Test that from_string() raises ValueError for invalid base58 alphabet characters.
        
        Base58 alphabet excludes: 0, O, I, l, +, / to avoid visual confusion.
        
        Args:
            invalid_alphabet_letters: String containing characters not in base58 alphabet.
            sample_wallet_vo: Fixture providing a valid WalletAddressVO instance (unused but required).
        """
        with pytest.raises(ValueError):
            WalletAddressVO.from_string(invalid_alphabet_letters)

    @pytest.mark.parametrize(
        "invalid_value",
        [
            True,
            None,
            -5,
            Decimal("55.55"),
            9000,
            [True, None, "string"],
        ],
    )
    def test_wallet_address_vo_from_string_with_non_string_raises_error(
        self,
        sample_wallet_vo: WalletAddressVO,
        invalid_value: Any,
    ) -> None:
        """Test that from_string() raises error when called with non-string value.
        
        Args:
            sample_wallet_vo: Fixture providing a valid WalletAddressVO instance (unused but required).
            invalid_value: Non-string value to test (bool, None, int, Decimal, list, etc.).
        """
        with pytest.raises(InvalidWalletAddressError):
            WalletAddressVO.from_string(invalid_value)


