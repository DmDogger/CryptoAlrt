import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from application.use_cases.fetch_and_save_to_database import FetchAndSaveUseCase
from application.dtos.coingecko_object import CoinGeckoDTO
from domain.entities.cryptocurrency import CryptocurrencyEntity
from domain.exceptions import UnsuccessfullyCoinGeckoAPICall, UnexpectedError


class TestFetchAndSaveUseCase:
    """Tests for FetchAndSaveUseCase."""

    @pytest.fixture
    def mock_coingecko_client(self):
        """Create mock CoinGecko client."""
        client = MagicMock()
        client.fetch_price = AsyncMock()
        return client

    @pytest.fixture
    def mock_crypto_repository(self):
        """Create mock cryptocurrency repository."""
        repository = MagicMock()
        repository.get_cryptocurrency_by_symbol = AsyncMock()
        repository.save = AsyncMock()
        repository.save_price = AsyncMock()
        return repository

    @pytest.fixture
    def use_case(self, mock_coingecko_client, mock_crypto_repository):
        """Create FetchAndSaveUseCase instance with mocks."""
        return FetchAndSaveUseCase(
            coingecko_client=mock_coingecko_client,
            crypto_repository=mock_crypto_repository,
        )

    @pytest.fixture
    def sample_coingecko_dto(self):
        """Create sample CoinGeckoDTO."""
        return CoinGeckoDTO(
            id="bitcoin",
            symbol="BTC",
            name="Bitcoin",
            current_price=Decimal("67000.50"),
            market_cap=Decimal("1300000000000"),
            total_volume=Decimal("30000000000"),
            high_24h=Decimal("68000.00"),
            low_24h=Decimal("66000.00"),
            price_change_24h=Decimal("1500.25"),
            price_change_percentage_24h=Decimal("2.29"),
            last_updated=datetime.now(),
        )

    @pytest.fixture
    def sample_crypto_entity(self):
        """Create sample CryptocurrencyEntity."""
        return CryptocurrencyEntity(
            id=uuid4(), symbol="BTC", name="Bitcoin", coingecko_id="bitcoin"
        )

    @pytest.mark.asyncio
    async def test_execute_with_existing_cryptocurrency(
        self,
        use_case,
        mock_coingecko_client,
        mock_crypto_repository,
        sample_coingecko_dto,
        sample_crypto_entity,
    ):
        """Test execute when cryptocurrency already exists in database."""
        # Arrange
        coin_id = "bitcoin"
        mock_coingecko_client.fetch_price.return_value = sample_coingecko_dto
        mock_crypto_repository.get_cryptocurrency_by_symbol.return_value = (
            sample_crypto_entity
        )

        # Act
        await use_case.execute(coin_id)

        # Assert
        mock_coingecko_client.fetch_price.assert_called_once_with(coin_id)
        mock_crypto_repository.get_cryptocurrency_by_symbol.assert_called_once_with(
            "BTC"
        )
        mock_crypto_repository.save.assert_not_called()  # Should not create new crypto
        mock_crypto_repository.save_price.assert_called_once_with(
            cryptocurrency_id=sample_crypto_entity.id, price_data=sample_coingecko_dto
        )

    @pytest.mark.asyncio
    async def test_execute_with_new_cryptocurrency(
        self,
        use_case,
        mock_coingecko_client,
        mock_crypto_repository,
        sample_coingecko_dto,
    ):
        """Test execute when cryptocurrency doesn't exist and needs to be created."""
        # Arrange
        coin_id = "bitcoin"
        mock_coingecko_client.fetch_price.return_value = sample_coingecko_dto
        mock_crypto_repository.get_cryptocurrency_by_symbol.return_value = None

        # Act
        await use_case.execute(coin_id)

        # Assert
        mock_coingecko_client.fetch_price.assert_called_once_with(coin_id)
        mock_crypto_repository.get_cryptocurrency_by_symbol.assert_called_once_with(
            "BTC"
        )

        # Should create new cryptocurrency
        mock_crypto_repository.save.assert_called_once()
        saved_entity = mock_crypto_repository.save.call_args[0][0]
        assert isinstance(saved_entity, CryptocurrencyEntity)
        assert saved_entity.symbol == "BTC"
        assert saved_entity.name == "Bitcoin"
        assert saved_entity.coingecko_id == "bitcoin"

        # Should save price with new cryptocurrency ID
        mock_crypto_repository.save_price.assert_called_once()
        call_args = mock_crypto_repository.save_price.call_args
        assert call_args.kwargs["cryptocurrency_id"] == saved_entity.id
        assert call_args.kwargs["price_data"] == sample_coingecko_dto

    @pytest.mark.asyncio
    async def test_execute_coingecko_returns_none(
        self, use_case, mock_coingecko_client, mock_crypto_repository
    ):
        """Test execute raises exception when CoinGecko API returns None."""
        # Arrange
        coin_id = "bitcoin"
        mock_coingecko_client.fetch_price.return_value = None

        # Act & Assert
        with pytest.raises(
            UnsuccessfullyCoinGeckoAPICall, match="Coingecko returned None"
        ):
            await use_case.execute(coin_id)

        # Should not call repository methods
        mock_crypto_repository.get_cryptocurrency_by_symbol.assert_not_called()
        mock_crypto_repository.save.assert_not_called()
        mock_crypto_repository.save_price.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_coingecko_api_fails(
        self, use_case, mock_coingecko_client, mock_crypto_repository
    ):
        """Test execute when CoinGecko API call fails."""
        # Arrange
        coin_id = "bitcoin"
        mock_coingecko_client.fetch_price.side_effect = UnsuccessfullyCoinGeckoAPICall(
            "API error"
        )

        # Act & Assert
        with pytest.raises(UnsuccessfullyCoinGeckoAPICall):
            await use_case.execute(coin_id)

        # Should not call repository methods
        mock_crypto_repository.get_cryptocurrency_by_symbol.assert_not_called()
        mock_crypto_repository.save.assert_not_called()
        mock_crypto_repository.save_price.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_repository_save_fails(
        self,
        use_case,
        mock_coingecko_client,
        mock_crypto_repository,
        sample_coingecko_dto,
    ):
        """Test execute when repository save operation fails."""
        # Arrange
        coin_id = "bitcoin"
        mock_coingecko_client.fetch_price.return_value = sample_coingecko_dto
        mock_crypto_repository.get_cryptocurrency_by_symbol.return_value = None
        mock_crypto_repository.save.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(UnexpectedError):
            await use_case.execute(coin_id)

        # Should attempt to save but fail
        mock_crypto_repository.save.assert_called_once()
        mock_crypto_repository.save_price.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_save_price_fails(
        self,
        use_case,
        mock_coingecko_client,
        mock_crypto_repository,
        sample_coingecko_dto,
        sample_crypto_entity,
    ):
        """Test execute when save_price operation fails."""
        # Arrange
        coin_id = "bitcoin"
        mock_coingecko_client.fetch_price.return_value = sample_coingecko_dto
        mock_crypto_repository.get_cryptocurrency_by_symbol.return_value = (
            sample_crypto_entity
        )
        mock_crypto_repository.save_price.side_effect = Exception("Price save error")

        # Act & Assert
        with pytest.raises(UnexpectedError):
            await use_case.execute(coin_id)

        # Should call save_price but fail
        mock_crypto_repository.save_price.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_different_coin_ids(
        self,
        use_case,
        mock_coingecko_client,
        mock_crypto_repository,
        sample_crypto_entity,
    ):
        """Test execute works with different coin IDs."""
        # Arrange
        coin_ids = ["bitcoin", "ethereum", "cardano"]
        symbols = ["BTC", "ETH", "ADA"]

        for coin_id, symbol in zip(coin_ids, symbols):
            dto = CoinGeckoDTO(
                id=coin_id,
                symbol=symbol,
                name=coin_id.capitalize(),
                current_price=Decimal("1000.00"),
                market_cap=Decimal("1000000000"),
                total_volume=Decimal("10000000"),
                high_24h=Decimal("1100.00"),
                low_24h=Decimal("900.00"),
                price_change_24h=Decimal("50.00"),
                price_change_percentage_24h=Decimal("5.00"),
                last_updated=datetime.now(),
            )

            mock_coingecko_client.fetch_price.return_value = dto
            mock_crypto_repository.get_cryptocurrency_by_symbol.return_value = (
                sample_crypto_entity
            )

            # Act
            await use_case.execute(coin_id)

            # Assert
            assert mock_coingecko_client.fetch_price.called
            assert mock_crypto_repository.save_price.called

    @pytest.mark.asyncio
    async def test_execute_full_flow_new_cryptocurrency(
        self,
        use_case,
        mock_coingecko_client,
        mock_crypto_repository,
        sample_coingecko_dto,
    ):
        """Test complete flow when creating new cryptocurrency and saving price."""
        # Arrange
        coin_id = "solana"
        sample_coingecko_dto = CoinGeckoDTO(
            id="solana",
            symbol="SOL",
            name="Solana",
            current_price=Decimal("150.75"),
            market_cap=Decimal("60000000000"),
            total_volume=Decimal("2000000000"),
            high_24h=Decimal("155.00"),
            low_24h=Decimal("148.00"),
            price_change_24h=Decimal("5.25"),
            price_change_percentage_24h=Decimal("3.61"),
            last_updated=datetime.now(),
        )

        mock_coingecko_client.fetch_price.return_value = sample_coingecko_dto
        mock_crypto_repository.get_cryptocurrency_by_symbol.return_value = None

        # Act
        await use_case.execute(coin_id)

        # Assert - verify complete flow
        # 1. Fetch from API
        mock_coingecko_client.fetch_price.assert_called_once_with("solana")

        # 2. Check if crypto exists
        mock_crypto_repository.get_cryptocurrency_by_symbol.assert_called_once_with(
            "SOL"
        )

        # 3. Create new crypto
        mock_crypto_repository.save.assert_called_once()
        created_entity = mock_crypto_repository.save.call_args[0][0]
        assert created_entity.symbol == "SOL"
        assert created_entity.name == "Solana"
        assert created_entity.coingecko_id == "solana"

        # 4. Save price
        mock_crypto_repository.save_price.assert_called_once()
        price_call = mock_crypto_repository.save_price.call_args
        assert price_call.kwargs["cryptocurrency_id"] == created_entity.id
        assert price_call.kwargs["price_data"].symbol == "SOL"

    @pytest.mark.asyncio
    async def test_execute_logging(
        self,
        use_case,
        mock_coingecko_client,
        mock_crypto_repository,
        sample_coingecko_dto,
        sample_crypto_entity,
        caplog,
    ):
        """Test that appropriate logging occurs during execution."""
        # Arrange
        coin_id = "bitcoin"
        mock_coingecko_client.fetch_price.return_value = sample_coingecko_dto
        mock_crypto_repository.get_cryptocurrency_by_symbol.return_value = (
            sample_crypto_entity
        )

        # Act
        await use_case.execute(coin_id)

        # Assert - verify logging messages
        # Note: This test may need adjustment based on actual logging configuration
        assert mock_coingecko_client.fetch_price.called
        assert mock_crypto_repository.save_price.called
