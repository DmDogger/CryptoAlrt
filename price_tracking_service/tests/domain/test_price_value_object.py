import pytest
from datetime import UTC, datetime
from decimal import Decimal

from domain.value_objects.price import PriceValueObject
from domain.exceptions import DomainValidationError


class TestPriceValueObject:
    """Tests for Price domain value object."""

    def test_create_valid_price(self):
        """Test creating a valid price."""
        price = PriceValueObject(
            cryptocurrency="BTC", price=Decimal("50000"), timestamp=datetime.now(UTC)
        )

        assert price.cryptocurrency == "BTC"
        assert price.price == Decimal("50000")
        assert isinstance(price.timestamp, datetime)

    def test_price_invalid_negative_price(self):
        """Test that negative price raises error."""
        with pytest.raises(DomainValidationError, match="Price must be positive"):
            PriceValueObject(
                cryptocurrency="BTC", price=Decimal("-100"), timestamp=datetime.now(UTC)
            )

    def test_price_invalid_zero_price(self):
        """Test that zero price raises error."""
        with pytest.raises(DomainValidationError, match="Price must be positive"):
            PriceValueObject(cryptocurrency="BTC", price=Decimal("0"), timestamp=datetime.now(UTC))

    def test_price_invalid_short_cryptocurrency(self):
        """Test that short cryptocurrency raises error."""
        with pytest.raises(
            DomainValidationError,
            match="Cryptocurrency symbol must be between 3 and 100 characters",
        ):
            PriceValueObject(
                cryptocurrency="BT", price=Decimal("50000"), timestamp=datetime.now(UTC)
            )

    def test_price_invalid_future_timestamp(self):
        """Test that future timestamp raises error."""
        future_time = datetime.now(UTC).replace(year=2030)
        with pytest.raises(DomainValidationError, match="Timestamp can't be in future"):
            PriceValueObject(cryptocurrency="BTC", price=Decimal("50000"), timestamp=future_time)

    def test_price_to_dict(self):
        """Test serialization to dict."""
        timestamp = datetime(2023, 1, 1, tzinfo=UTC)
        price = PriceValueObject(cryptocurrency="BTC", price=Decimal("50000"), timestamp=timestamp)

        data = price.to_dict()
        assert data["cryptocurrency"] == "BTC"
        assert data["price"] == "50000"
        assert data["timestamp"] == timestamp.isoformat()
        assert data["timestamp"] == timestamp.isoformat()

    def test_price_eq_with_numbers(self):
        """Test __eq__ compares price value with numbers."""
        price = PriceValueObject(
            cryptocurrency="BTC", price=Decimal("50000"), timestamp=datetime.now(UTC)
        )

        assert (price == Decimal("50000")) is True
        assert (price == 50000) is True
        assert (price == 50000.0) is True
        assert (price == Decimal("51000")) is False
        assert (price == "50000") is False

    def test_price_calculate_change_price_percent_increase(self):
        """Test calculating price change percent for increase."""
        price = PriceValueObject(
            cryptocurrency="BTC", price=Decimal("50000"), timestamp=datetime.now(UTC)
        )

        result = PriceValueObject.calculate_change_price_percent_(
            old_price=price.price, new_price=Decimal("55000")
        )
        assert result == Decimal("10")  # (55000 - 50000) / 50000 * 100 = 10

    def test_price_calculate_change_price_percent_decrease(self):
        """Test calculating price change percent for decrease."""
        price = PriceValueObject(
            cryptocurrency="BTC", price=Decimal("50000"), timestamp=datetime.now(UTC)
        )

        result = PriceValueObject.calculate_change_price_percent_(
            old_price=price.price, new_price=Decimal("45000")
        )
        assert result == Decimal("-10")  # (45000 - 50000) / 50000 * 100 = -10

    def test_price_calculate_change_price_percent_no_change(self):
        """Test calculating price change percent for no change."""
        price = PriceValueObject(
            cryptocurrency="BTC", price=Decimal("50000"), timestamp=datetime.now(UTC)
        )

        result = PriceValueObject.calculate_change_price_percent_(
            old_price=price.price, new_price=Decimal("50000")
        )
        assert result == Decimal("0")

    def test_price_calculate_change_price_percent_with_float(self):
        """Test calculating price change percent with Decimal converted from float."""
        price = PriceValueObject(
            cryptocurrency="BTC", price=Decimal("50000"), timestamp=datetime.now(UTC)
        )

        result = PriceValueObject.calculate_change_price_percent_(
            old_price=price.price, new_price=Decimal("52500.0")
        )
        assert result == Decimal("5")  # (52500 - 50000) / 50000 * 100 = 5

    def test_price_calculate_change_price_percent_with_int(self):
        """Test calculating price change percent with Decimal converted from int."""
        price = PriceValueObject(
            cryptocurrency="BTC", price=Decimal("50000"), timestamp=datetime.now(UTC)
        )

        result = PriceValueObject.calculate_change_price_percent_(
            old_price=price.price, new_price=Decimal("60000")
        )
        assert result == Decimal("20")  # (60000 - 50000) / 50000 * 100 = 20

    def test_calculate_change_price_percent_static_call(self):
        """Test that calculate_change_price_percent_ can be called statically without instance."""
        result = PriceValueObject.calculate_change_price_percent_(
            old_price=Decimal("100"), new_price=Decimal("120")
        )
        assert result == Decimal("20")  # (120 - 100) / 100 * 100 = 20

    def test_price_immutable(self):
        """Test that Price is immutable."""
        price = PriceValueObject(
            cryptocurrency="BTC", price=Decimal("50000"), timestamp=datetime.now(UTC)
        )

        with pytest.raises(AttributeError):
            price.price = Decimal("51000")

    def test_price_hash(self):
        """Test that Price is hashable."""
        price = PriceValueObject(
            cryptocurrency="BTC", price=Decimal("50000"), timestamp=datetime.now(UTC)
        )

        # Should not raise error
        hash(price)
