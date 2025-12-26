"""Tests for NonceVO value object."""

import pytest
from domain.value_objects.nonce_vo import NonceVO
from domain.exceptions import NonceValidationError


class TestNonceVO:
    """Test suite for NonceVO value object."""

    def test_create_valid_nonce_vo(
        self,
        sample_nonce_vo: NonceVO,
    ) -> None:
        """Test that a valid NonceVO can be created from fixture.
        
        Args:
            sample_nonce_vo: Fixture providing a valid NonceVO instance.
        """
        assert sample_nonce_vo is not None
        assert isinstance(sample_nonce_vo, NonceVO)

    @pytest.mark.parametrize(
        "invalid_length",
        [
            ".",
            "..",
            "TstNonc",
        ],
    )
    def test_incorrect_length_nonce(
        self,
        invalid_length: str,
        sample_nonce_vo: NonceVO,
    ) -> None:
        """Test that creating NonceVO with length < 8 characters raises error.
        
        Args:
            invalid_length: Nonce value shorter than 8 characters.
            sample_nonce_vo: Fixture providing a valid NonceVO instance (unused but required).
        """
        with pytest.raises(NonceValidationError):
            NonceVO(value=invalid_length)

    def test_nonce_creates_unique_values(
        self,
        sample_nonce_vo: NonceVO,
    ) -> None:
        """Test that generate() method creates unique nonce values.
        
        Args:
            sample_nonce_vo: Fixture providing a valid NonceVO instance.
        """
        is_unique = NonceVO.generate()
        is_unique_too = NonceVO.generate()

        assert is_unique != is_unique_too
        assert is_unique.value != is_unique_too.value

    def test_nonce_vo_empty_value_raises_error(
        self,
        sample_nonce_vo: NonceVO,
    ) -> None:
        """Test that creating NonceVO with empty value raises error.
        
        Args:
            sample_nonce_vo: Fixture providing a valid NonceVO instance (unused but required).
        """
        with pytest.raises(NonceValidationError):
            NonceVO(value="")

    def test_nonce_vo_generate_creates_valid_nonce(
        self,
        sample_nonce_vo: NonceVO,
    ) -> None:
        """Test that generate() method creates a valid NonceVO instance.
        
        Args:
            sample_nonce_vo: Fixture providing a valid NonceVO instance (unused but required).
        """
        valid_value = NonceVO.generate()

        assert isinstance(valid_value, NonceVO)
        assert valid_value.value is not None
        assert len(valid_value.value) >= 8

    def test_nonce_vo_generate_has_minimum_length(
        self,
        sample_nonce_vo: NonceVO,
    ) -> None:
        """Test that generate() method creates nonce with length >= 8 characters.
        
        Args:
            sample_nonce_vo: Fixture providing a valid NonceVO instance (unused but required).
        """
        valid_length = NonceVO.generate()

        assert len(valid_length.value) >= 8