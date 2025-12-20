import pytest
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from infrastructures.mappers.alert import InfrastructureAlertMapper
from application.dtos.alert import AlertDTO
from domain.value_objects.threshold import ThresholdValueObject


class TestInfrastructureAlertMapper:
    """Tests for InfrastructureAlertMapper."""

    def test_to_dict(self):
        """Test serialization of AlertDTO to dict."""
        threshold = ThresholdValueObject(value=Decimal("50000"))
        dto = AlertDTO(
            id=uuid4(),
            email="user@example.com",
            cryptocurrency="BTC",
            threshold_price=threshold,
            is_active=True,
            created_at=datetime(2023, 1, 1, tzinfo=UTC)
        )

        mapper = InfrastructureAlertMapper()
        data = mapper.to_dict(dto)

        assert data["id"] == str(dto.id)
        assert data["email"] == "user@example.com"
        assert data["cryptocurrency"] == "BTC"
        assert data["threshold_price"]["value"] == "50000"
        assert data["is_active"] is True
        assert data["created_at"] == "2023-01-01T00:00:00+00:00"

    def test_from_dict(self):
        """Test deserialization from dict to AlertDTO."""
        data = {
            "id": "12345678-1234-5678-9012-123456789012",
            "email": "user@example.com",
            "cryptocurrency": "BTC",
            "threshold_price": {"value": "50000"},
            "is_active": True,
            "created_at": "2023-01-01T00:00:00+00:00"
        }

        mapper = InfrastructureAlertMapper()
        dto = mapper.from_dict(data)

        assert str(dto.id) == "12345678-1234-5678-9012-123456789012"
        assert dto.email == "user@example.com"
        assert dto.cryptocurrency == "BTC"
        assert dto.threshold_price.value == Decimal("50000")
        assert dto.is_active is True
        assert dto.created_at == datetime(2023, 1, 1, tzinfo=UTC)