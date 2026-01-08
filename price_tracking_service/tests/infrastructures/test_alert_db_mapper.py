import pytest
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4
from unittest import mock
from unittest.mock import MagicMock

from domain.entities.alert import AlertEntity
from domain.value_objects.threshold import ThresholdValueObject


class TestAlertDBMapper:
    """Tests for AlertDBMapper."""

    @pytest.fixture
    def mapper(self):
        """Create AlertDBMapper instance."""
        from infrastructures.database.mappers.alert_db_mapper import AlertDBMapper

        return AlertDBMapper()

    def test_to_database_model(self, mapper):
        """Test conversion from AlertEntity to Alert database model."""
        entity = AlertEntity(
            id=uuid4(),
            email="user@example.com",
            telegram_id=None,
            cryptocurrency="BTC",
            threshold_price=ThresholdValueObject(value=Decimal("50000")),
            is_triggered=False,
            is_active=True,
            created_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC),
        )
        cryptocurrency_id = uuid4()

        with mock.patch(
            "src.infrastructures.database.mappers.alert_db_mapper.Alert"
        ) as mock_model_class:
            result = mapper.to_database_model(entity, cryptocurrency_id)
            call_kwargs = mock_model_class.call_args[1]
            assert call_kwargs["id"] == entity.id
            assert call_kwargs["email"] == entity.email
            assert call_kwargs["cryptocurrency_id"] == cryptocurrency_id
            assert call_kwargs["threshold_price"] == entity.threshold_price.value
            assert call_kwargs["is_active"] == entity.is_active
            assert call_kwargs["created_at"] == entity.created_at

    def test_from_database_model(self, mapper):
        """Test conversion from Alert database model to AlertEntity."""
        # Create mock model
        model = MagicMock()
        model.id = uuid4()
        model.email = "user@example.com"
        model.threshold_price = Decimal("50000")
        model.is_active = True
        model.created_at = datetime(2023, 1, 1, 12, 0, 0)

        # Mock cryptocurrency relationship
        mock_crypto = MagicMock()
        mock_crypto.symbol = "BTC"
        model.cryptocurrency = mock_crypto

        entity = mapper.from_database_model(model)

        assert entity.id == model.id
        assert entity.email == model.email
        assert entity.cryptocurrency == "BTC"  # From relationship
        assert entity.threshold_price.value == model.threshold_price
        assert entity.is_active == model.is_active

    def test_from_database_model_missing_relationship(self, mapper):
        """Test that from_database_model raises error if relationship not loaded."""
        model = MagicMock()
        model.id = uuid4()
        model.email = "user@example.com"
        model.cryptocurrency_id = uuid4()
        model.threshold_price = Decimal("50000")
        model.is_active = True
        model.created_at = datetime(2023, 1, 1, 12, 0, 0)
        model.cryptocurrency = None  # Relationship not loaded

        with pytest.raises(ValueError, match="Cryptocurrency relationship must be loaded"):
            mapper.from_database_model(model)
