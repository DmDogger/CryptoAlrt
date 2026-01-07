import pytest
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from domain.entities.alert import AlertEntity
from domain.value_objects.threshold import ThresholdValueObject
from domain.exceptions import DomainValidationError


class TestAlertEntity:
    """Tests for AlertEntity domain entity."""

    def test_create_valid_alert(self):
        """Test creating a valid alert with all required fields."""
        threshold = ThresholdValueObject(value=Decimal("50000"))
        alert = AlertEntity(
            id=uuid4(),
            email="user@example.com",
            telegram_id=None,
            cryptocurrency="BTC",
            threshold_price=threshold,
            is_triggered=False,
            is_active=True,
            created_at=datetime.now(UTC),
        )

        assert alert.email == "user@example.com"
        assert alert.cryptocurrency == "BTC"
        assert alert.threshold_price.value == Decimal("50000")
        assert alert.is_active is True
        assert isinstance(alert.id, UUID)

    def test_alert_with_invalid_email(self):
        """Test that invalid email raises DomainValidationError."""
        threshold = ThresholdValueObject(value=Decimal("50000"))

        with pytest.raises(DomainValidationError, match="Invalid email format"):
            AlertEntity(
                id=uuid4(),
                email="invalid-email",
                telegram_id=None,
                cryptocurrency="BTC",
                threshold_price=threshold,
                is_triggered=False,
                is_active=True,
                created_at=datetime.now(UTC),
            )

    def test_alert_with_short_cryptocurrency(self):
        """Test that cryptocurrency shorter than 3 characters raises error."""
        threshold = ThresholdValueObject(value=Decimal("50000"))

        with pytest.raises(
            DomainValidationError,
            match="Cryptocurrency symbol must be between 3 and 100 characters",
        ):
            AlertEntity(
                id=uuid4(),
                email="user@example.com",
                telegram_id=None,
                cryptocurrency="BT",
                threshold_price=threshold,
                is_triggered=False,
                is_active=True,
                created_at=datetime.now(UTC),
            )

    def test_alert_with_long_cryptocurrency(self):
        """Test that cryptocurrency longer than 100 characters raises error."""
        threshold = ThresholdValueObject(value=Decimal("50000"))
        long_crypto = "A" * 101

        with pytest.raises(
            DomainValidationError,
            match="Cryptocurrency symbol must be between 3 and 100 characters",
        ):
            AlertEntity(
                id=uuid4(),
                email="user@example.com",
                telegram_id=None,
                cryptocurrency=long_crypto,
                threshold_price=threshold,
                is_triggered=False,
                is_active=True,
                created_at=datetime.now(UTC),
            )

    def test_alert_immutable(self):
        """Test that AlertEntity is immutable (frozen dataclass)."""
        threshold = ThresholdValueObject(value=Decimal("50000"))
        alert = AlertEntity(
            id=uuid4(),
            email="user@example.com",
            telegram_id=None,
            cryptocurrency="BTC",
            threshold_price=threshold,
            is_triggered=False,
            is_active=True,
            created_at=datetime.now(UTC),
        )

        with pytest.raises(AttributeError):
            alert.is_active = False

    def test_alert_created_at_default(self):
        """Test that created_at has default value."""
        threshold = ThresholdValueObject(value=Decimal("50000"))
        alert = AlertEntity(
            id=uuid4(),
            email="user@example.com",
            telegram_id=None,
            cryptocurrency="BTC",
            threshold_price=threshold,
            is_triggered=False,
            is_active=True,
            # created_at not provided, should use default
        )

        assert isinstance(alert.created_at, datetime)
