import pytest
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from application.dtos.alert import AlertDTO
from domain.value_objects.threshold import ThresholdValueObject


class TestAlertDTO:
    """Tests for AlertDTO application DTO."""

    def test_create_valid_alert_dto(self):
        """Test creating a valid AlertDTO."""
        threshold = ThresholdValueObject(value=Decimal("50000"))
        dto = AlertDTO(
            id=uuid4(),
            email="user@example.com",
            cryptocurrency="BTC",
            threshold_price=threshold,
            is_active=True,
            created_at=datetime.now(UTC)
        )

        assert dto.email == "user@example.com"
        assert dto.cryptocurrency == "BTC"
        assert dto.threshold_price.value == Decimal("50000")
        assert dto.is_active is True

    def test_alert_dto_immutable(self):
        """Test that AlertDTO is immutable."""
        threshold = ThresholdValueObject(value=Decimal("50000"))
        dto = AlertDTO(
            id=uuid4(),
            email="user@example.com",
            cryptocurrency="BTC",
            threshold_price=threshold,
            is_active=True,
            created_at=datetime.now(UTC)
        )

        with pytest.raises(AttributeError):
            dto.is_active = False