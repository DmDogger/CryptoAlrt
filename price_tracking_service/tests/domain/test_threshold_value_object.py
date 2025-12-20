import pytest
from decimal import Decimal

from domain.value_objects.threshold import ThresholdValueObject
from domain.exceptions import DomainValidationError


class TestThresholdValueObject:
    """Tests for ThresholdValueObject domain value object."""

    def test_create_valid_threshold(self):
        """Test creating a valid threshold."""
        threshold = ThresholdValueObject(value=Decimal("50000"))

        assert threshold.value == Decimal("50000")

    def test_threshold_invalid_negative_value(self):
        """Test that negative value raises error."""
        with pytest.raises(DomainValidationError, match="Threshold value must be positive"):
            ThresholdValueObject(value=Decimal("-100"))

    def test_threshold_invalid_zero_value(self):
        """Test that zero value raises error."""
        with pytest.raises(DomainValidationError, match="Threshold value must be positive"):
            ThresholdValueObject(value=Decimal("0"))

    def test_threshold_is_above_true(self):
        """Test is_above returns True when price > threshold."""
        threshold = ThresholdValueObject(value=Decimal("50000"))
        assert threshold.is_above(Decimal("51000")) is True

    def test_threshold_is_above_false(self):
        """Test is_above returns False when price <= threshold."""
        threshold = ThresholdValueObject(value=Decimal("50000"))
        assert threshold.is_above(Decimal("50000")) is False
        assert threshold.is_above(Decimal("49000")) is False

    def test_threshold_is_below_true(self):
        """Test is_below returns True when price < threshold."""
        threshold = ThresholdValueObject(value=Decimal("50000"))
        assert threshold.is_below(Decimal("49000")) is True

    def test_threshold_is_below_false(self):
        """Test is_below returns False when price >= threshold."""
        threshold = ThresholdValueObject(value=Decimal("50000"))
        assert threshold.is_below(Decimal("50000")) is False
        assert threshold.is_below(Decimal("51000")) is False

    def test_threshold_is_equal_true(self):
        """Test is_equal returns True when price == threshold."""
        threshold = ThresholdValueObject(value=Decimal("50000"))
        assert threshold.is_equal(Decimal("50000")) is True

    def test_threshold_is_equal_false(self):
        """Test is_equal returns False when price != threshold."""
        threshold = ThresholdValueObject(value=Decimal("50000"))
        assert threshold.is_equal(Decimal("51000")) is False

    def test_threshold_to_dict(self):
        """Test serialization to dict."""
        threshold = ThresholdValueObject(value=Decimal("50000"))
        data = threshold.to_dict()
        assert data == {"value": "50000"}

    def test_threshold_eq_with_decimal(self):
        """Test __eq__ with Decimal."""
        threshold = ThresholdValueObject(value=Decimal("50000"))
        assert (threshold == Decimal("50000")) is True
        assert (threshold == Decimal("51000")) is False

    def test_threshold_eq_with_int(self):
        """Test __eq__ with int."""
        threshold = ThresholdValueObject(value=Decimal("50000"))
        assert (threshold == 50000) is True
        assert (threshold == 51000) is False

    def test_threshold_eq_with_float(self):
        """Test __eq__ with float."""
        threshold = ThresholdValueObject(value=Decimal("50000"))
        assert (threshold == 50000.0) is True
        assert (threshold == 51000.0) is False

    def test_threshold_eq_with_other_threshold(self):
        """Test __eq__ with another Threshold."""
        threshold1 = ThresholdValueObject(value=Decimal("50000"))
        threshold2 = ThresholdValueObject(value=Decimal("50000"))
        threshold3 = ThresholdValueObject(value=Decimal("51000"))

        assert (threshold1 == threshold2) is True
        assert (threshold1 == threshold3) is False

    def test_threshold_eq_with_invalid_type(self):
        """Test __eq__ with invalid type returns False."""
        threshold = ThresholdValueObject(value=Decimal("50000"))
        assert (threshold == "50000") is False
        assert (threshold == [50000]) is False

    def test_threshold_immutable(self):
        """Test that Threshold is immutable."""
        threshold = ThresholdValueObject(value=Decimal("50000"))

        with pytest.raises(AttributeError):
            threshold.value = Decimal("51000")

    def test_threshold_hash(self):
        """Test that Threshold is hashable."""
        threshold = ThresholdValueObject(value=Decimal("50000"))
        # Should not raise error
        hash(threshold)