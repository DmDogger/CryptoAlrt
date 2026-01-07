import pytest
from datetime import UTC, datetime
from uuid import uuid4

from application.dtos.cryptocurrency import CryptocurrencyDTO


class TestCryptocurrencyDTO:
    """Tests for CryptocurrencyDTO application DTO."""

    def test_create_valid_cryptocurrency_dto(self):
        """Test creating a valid CryptocurrencyDTO."""
        dto = CryptocurrencyDTO(
            id=uuid4(), symbol="BTC", name="Bitcoin", created_at=datetime.now(UTC)
        )

        assert dto.symbol == "BTC"
        assert dto.name == "Bitcoin"

    def test_cryptocurrency_dto_immutable(self):
        """Test that CryptocurrencyDTO is immutable."""
        dto = CryptocurrencyDTO(
            id=uuid4(), symbol="BTC", name="Bitcoin", created_at=datetime.now(UTC)
        )

        with pytest.raises(AttributeError):
            dto.name = "Ethereum"
