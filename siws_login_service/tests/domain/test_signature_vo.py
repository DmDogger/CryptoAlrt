"""Tests for SignatureVO value object."""

from typing import Any

import pytest
from domain.value_objects.signature_vo import SignatureVO
from domain.exceptions import SignatureValidationError


class TestSignatureVO:
    """Test suite for SignatureVO value object."""

    def test_create_valid_signature_vo(
        self,
        sample_signature_vo: SignatureVO,
    ) -> None:
        """Test that a valid SignatureVO can be created from fixture.
        
        Args:
            sample_signature_vo: Fixture providing a valid SignatureVO instance.
        """
        assert sample_signature_vo is not None
        assert isinstance(sample_signature_vo, SignatureVO)

    def test_signature_vo_from_string_creates_valid_instance(
        self,
        sample_signature_vo: SignatureVO,
    ) -> None:
        """Test that from_string() factory method creates valid SignatureVO instance.
        
        Args:
            sample_signature_vo: Fixture providing a valid SignatureVO instance (unused but required).
        """
        valid_signature = sample_signature_vo.value
        correct_instance = SignatureVO.from_string(valid_signature)

        assert isinstance(correct_instance, SignatureVO)
        assert correct_instance.value == valid_signature

    def test_correct_signature_to_bytes(
        self,
        sample_signature_vo: SignatureVO,
    ) -> None:
        """Test that to_bytes() method returns correct byte representation.
        
        Args:
            sample_signature_vo: Fixture providing a valid SignatureVO instance.
        """
        bytes_signature = sample_signature_vo.to_bytes()

        assert bytes_signature is not None
        assert isinstance(bytes_signature, bytes)
        assert len(bytes_signature) == 64

    @pytest.mark.parametrize(
        "invalid_length",
        [
            "5cRypRAdKEUtMCyFdqtEifWER5GMCfVnhZ8EUtcB7Sc3",
            "5" * 10,
            "",
        ],
    )
    def test_signature_vo_invalid_length_raises_error(
        self,
        invalid_length: str,
    ) -> None:
        """Test that from_string() raises error for invalid signature length.
        
        Args:
            invalid_length: Invalid signature string (wrong decoded length, not 64 bytes).
        """
        with pytest.raises(SignatureValidationError):
            SignatureVO.from_string(invalid_length)

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
    def test_signature_vo_invalid_base58_raises_error(
        self,
        invalid_alphabet_letters: str,
    ) -> None:
        """Test that from_string() raises ValueError for invalid base58 alphabet characters.
        
        Base58 alphabet excludes: 0, O, I, l, +, / to avoid visual confusion.
        
        Args:
            invalid_alphabet_letters: String containing characters not in base58 alphabet.
        """
        with pytest.raises(ValueError):
            SignatureVO.from_string(invalid_alphabet_letters)

    @pytest.mark.parametrize(
        "invalid_value",
        [
            True,
            None,
            -5,
            9000,
            [True, None, "string"],
        ],
    )
    def test_signature_vo_from_string_with_non_string_raises_error(
        self,
        invalid_value: Any,
    ) -> None:
        """Test that from_string() raises error when called with non-string value.
        
        Args:
            invalid_value: Non-string value to test (bool, None, int, list, etc.).
        """
        with pytest.raises(SignatureValidationError):
            SignatureVO.from_string(invalid_value)

