import pytest
from datetime import UTC, datetime
from uuid import uuid4
from unittest import mock
from unittest.mock import MagicMock

from src.domain.entities.cryptocurrency import CryptocurrencyEntity


class TestCryptocurrencyDBMapper:
    """Tests for CryptocurrencyDBMapper."""

    @pytest.fixture
    def mapper(self):
        """Create CryptocurrencyDBMapper instance."""
        from src.infrastructures.database.mappers.cryptocurrency_db_mapper import CryptocurrencyDBMapper
        return CryptocurrencyDBMapper()

    def test_to_database_model(self, mapper):
        """Test conversion from CryptocurrencyEntity to Cryptocurrency database model."""
        entity = CryptocurrencyEntity(
            id=uuid4(),
            symbol="BTC",
            name="Bitcoin",
            created_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
        )

        # Mock the Cryptocurrency model to avoid SQLAlchemy initialization issues
        with mock.patch('src.infrastructures.database.mappers.cryptocurrency_db_mapper.Cryptocurrency') as mock_model_class:
            mock_model = MagicMock()
            mock_model_class.return_value = mock_model
            
            result = mapper.to_database_model(entity)
            
            # Verify the model was created with correct parameters
            mock_model_class.assert_called_once()
            call_kwargs = mock_model_class.call_args[1]
            assert call_kwargs['id'] == entity.id
            assert call_kwargs['symbol'] == entity.symbol
            assert call_kwargs['name'] == entity.name
            # Timezone should be removed
            assert call_kwargs['created_at'] == entity.created_at.replace(tzinfo=None)

    def test_to_database_model_without_timezone(self, mapper):
        """Test conversion when entity has no timezone."""
        entity = CryptocurrencyEntity(
            id=uuid4(),
            symbol="ETH",
            name="Ethereum",
            created_at=datetime(2023, 1, 1, 12, 0, 0)  # No timezone
        )

        with mock.patch('src.infrastructures.database.mappers.cryptocurrency_db_mapper.Cryptocurrency') as mock_model_class:
            result = mapper.to_database_model(entity)
            call_kwargs = mock_model_class.call_args[1]
            assert call_kwargs['created_at'] == entity.created_at

    def test_from_database_model(self, mapper):
        """Test conversion from Cryptocurrency database model to CryptocurrencyEntity."""
        # Create mock model
        model = MagicMock()
        model.id = uuid4()
        model.symbol = "BTC"
        model.name = "Bitcoin"
        # Create datetime without timezone
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
