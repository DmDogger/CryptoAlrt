import pytest
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4
from unittest.mock import MagicMock

from domain.entities.alert import AlertEntity
from domain.value_objects.threshold import ThresholdValueObject


class TestAlertDBMapper:
    """Tests for AlertDBMapper."""

    @pytest.fixture(autouse=True)
    def _import_models(self):
        """Import all models to ensure SQLAlchemy relationships are initialized."""
        from infrastructures.database.models.cryptocurrency import Cryptocurrency  # noqa: F401
        from infrastructures.database.models.alert import Alert  # noqa: F401

    @pytest.fixture
    def mapper(self):
        """Create AlertDBMapper instance."""
        from infrastructures.database.mappers.alert_db_mapper import AlertDBMapper

        return AlertDBMapper()

    def test_to_database_model(self, mapper):
        """Test conversion from AlertEntity to Alert database model."""
        from infrastructures.database.models.alert import Alert

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

        result = mapper.to_database_model(entity, cryptocurrency_id)

        assert isinstance(result, Alert)
        assert result.id == entity.id
        assert result.email == entity.email
        assert result.cryptocurrency_id == cryptocurrency_id
        assert result.threshold_price == entity.threshold_price.value
        assert result.is_active == entity.is_active
        assert result.created_at == entity.created_at
        assert result.telegram_id == entity.telegram_id
        assert result.is_triggered == entity.is_triggered

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
