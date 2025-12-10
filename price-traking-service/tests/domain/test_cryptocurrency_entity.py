import pytest
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.domain.entities.cryptocurrency import CryptocurrencyEntity
from src.domain.exceptions import DomainValidationError


class TestCryptocurrencyEntity:
    """Tests for CryptocurrencyEntity domain entity."""

    def test_create_valid_cryptocurrency(self):
        """Test creating a valid cryptocurrency."""
        crypto = CryptocurrencyEntity(
            id=uuid4(),
            symbol="BTC",
            name="Bitcoin",
            created_at=datetime.now(UTC)
        )

        assert crypto.symbol == "BTC"
        assert crypto.name == "Bitcoin"
        assert isinstance(crypto.id, UUID)

    def test_create_cryptocurrency_with_factory(self):
        """Test creating cryptocurrency using create method."""
        crypto = CryptocurrencyEntity.create("ETH", "Ethereum")

        assert crypto.symbol == "ETH"
        assert crypto.name == "Ethereum"
        # No is_active field
        assert isinstance(crypto.id, UUID)

    def test_cryptocurrency_invalid_symbol_too_short(self):
        """Test that symbol shorter than 3 characters raises error."""
        with pytest.raises(DomainValidationError, match="Symbol must be"):
            CryptocurrencyEntity(
                id=uuid4(),
                symbol="BT",
                name="Bitcoin",
                created_at=datetime.now(UTC)
            )

    def test_cryptocurrency_invalid_symbol_too_long(self):
        """Test that symbol longer than 10 characters raises error."""
        with pytest.raises(DomainValidationError, match="Symbol must be"):
            CryptocurrencyEntity(
                id=uuid4(),
                symbol="VERYLONGCRYPTOSYMBOL",
                name="Bitcoin",
                created_at=datetime.now(UTC)
            )

    def test_cryptocurrency_invalid_symbol_lowercase(self):
        """Test that lowercase symbol raises error (assuming validation requires uppercase)."""
        # Note: Depending on regex, this might pass or fail
        with pytest.raises(DomainValidationError):
            CryptocurrencyEntity(
                id=uuid4(),
                symbol="btc",
                name="Bitcoin",
                created_at=datetime.now(UTC)
            )

    def test_cryptocurrency_invalid_name_too_short(self):
        """Test that name shorter than 2 characters raises error."""
        with pytest.raises(DomainValidationError, match="Name must be at least 2 characters"):
            CryptocurrencyEntity(
                id=uuid4(),
                symbol="BTC",
                name="B",
                created_at=datetime.now(UTC)
            )

    def test_cryptocurrency_to_dict(self):
        """Test serialization to dict."""
        crypto = CryptocurrencyEntity(
            id=uuid4(),
            symbol="BTC",
            name="Bitcoin",
            created_at=datetime(2023, 1, 1, tzinfo=UTC)
        )

        data = crypto.to_dict()
        assert data["id"] == str(crypto.id)
        assert data["symbol"] == "BTC"
        assert data["name"] == "Bitcoin"
        assert "created_at" in data

    def test_cryptocurrency_immutable(self):
        """Test that CryptocurrencyEntity is immutable."""
        crypto = CryptocurrencyEntity(
            id=uuid4(),
            symbol="BTC",
            name="Bitcoin",
            created_at=datetime.now(UTC)
        )

        with pytest.raises(AttributeError):
            crypto.name = "Ethereum"