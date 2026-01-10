from datetime import UTC, datetime
from uuid import uuid4
from unittest.mock import MagicMock

import pytest

from domain.entities.cryptocurrency import CryptocurrencyEntity


class TestCryptocurrencyDBMapper:
    """Tests for CryptocurrencyDBMapper."""

    @pytest.fixture(autouse=True)
    def _import_models(self):
        """Import all models to ensure SQLAlchemy relationships are initialized."""
        from infrastructures.database.models.cryptocurrency import Cryptocurrency  # noqa: F401
        from infrastructures.database.models.alert import Alert  # noqa: F401

    @pytest.fixture
    def mapper(self):
        """Create CryptocurrencyDBMapper instance."""
        from infrastructures.database.mappers.cryptocurrency_db_mapper import (
            CryptocurrencyDBMapper,
        )

        return CryptocurrencyDBMapper()

    def test_to_database_model(self, mapper):
        """Test conversion from CryptocurrencyEntity to Cryptocurrency database model."""
        from infrastructures.database.models.cryptocurrency import Cryptocurrency

        entity = CryptocurrencyEntity(
            id=uuid4(),
            symbol="BTC",
            name="Bitcoin",
            coingecko_id="bitcoin",
            created_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC),
        )

        result = mapper.to_database_model(entity)

        # Verify the model was created with correct parameters
        assert isinstance(result, Cryptocurrency)
        assert result.id == entity.id
        assert result.symbol == entity.symbol
        assert result.name == entity.name
        assert result.coingecko_id == entity.coingecko_id
        # Timezone should be removed
        assert result.created_at == entity.created_at.replace(tzinfo=None)

    def test_to_database_model_without_timezone(self, mapper):
        """Test conversion when entity has no timezone."""
        from infrastructures.database.models.cryptocurrency import Cryptocurrency

        entity = CryptocurrencyEntity(
            id=uuid4(),
            symbol="ETH",
            name="Ethereum",
            coingecko_id="ethereum",
            created_at=datetime(2023, 1, 1, 12, 0, 0),  # No timezone
        )

        result = mapper.to_database_model(entity)

        assert isinstance(result, Cryptocurrency)
        assert result.created_at == entity.created_at

    def test_from_database_model(self, mapper):
        """Test conversion from Cryptocurrency database model to CryptocurrencyEntity."""
        model = MagicMock()
        model.id = uuid4()
        model.symbol = "BTC"
        model.name = "Bitcoin"
        naive_dt = datetime(2023, 1, 1, 12, 0, 0)
        model.created_at = naive_dt

        entity = mapper.from_database_model(model)

        assert entity.id == model.id
        assert entity.symbol == model.symbol
        assert entity.name == model.name
        # Timezone should be added (UTC)
        assert entity.created_at.replace(tzinfo=None) == model.created_at
        assert entity.created_at.tzinfo == UTC

    def test_from_database_model_with_timezone(self, mapper):
        """Test conversion when model has timezone."""
        from datetime import timezone

        model = MagicMock()
        model.id = uuid4()
        model.symbol = "ETH"
        model.name = "Ethereum"
        model.created_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        entity = mapper.from_database_model(model)

        assert entity.created_at.tzinfo is not None
