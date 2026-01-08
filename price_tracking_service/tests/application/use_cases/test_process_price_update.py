import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from application.use_cases.process_price_update import ProcessPriceUpdateUseCase
from domain.entities.cryptocurrency import CryptocurrencyEntity
from domain.exceptions import (
    UnsuccessfullyCoinGeckoAPICall,
    RepositoryError,
    PublishError,
    UnexpectedError,
)


class TestProcessPriceUpdateUseCase:
    """Tests for ProcessPriceUpdateUseCase."""

    @pytest.fixture
    def mock_fetch_and_save_use_case(self):
        """Create mock FetchAndSaveUseCase."""
        use_case = MagicMock()
        use_case.execute = AsyncMock()
        return use_case

    @pytest.fixture
    def mock_publish_use_case(self):
        """Create mock PublishPriceUpdateToBrokerUseCase."""
        use_case = MagicMock()
        use_case.execute = AsyncMock()
        return use_case

    @pytest.fixture
    def mock_check_threshold_use_case(self):
        """Create mock CheckThresholdUseCase."""
        use_case = MagicMock()
        use_case.execute = AsyncMock()
        return use_case

    @pytest.fixture
    def use_case(
        self,
        mock_fetch_and_save_use_case,
        mock_publish_use_case,
        mock_check_threshold_use_case,
    ):
        """Create ProcessPriceUpdateUseCase instance with mocks."""
        return ProcessPriceUpdateUseCase(
            fetch_and_save_use_case=mock_fetch_and_save_use_case,
            publish_price_updated_use_case=mock_publish_use_case,
            check_threshold_use_case=mock_check_threshold_use_case,
        )

    @pytest.fixture
    def sample_crypto_entity(self):
        """Create sample CryptocurrencyEntity."""
        return CryptocurrencyEntity(
            id=uuid4(), symbol="BTC", name="Bitcoin", coingecko_id="bitcoin"
        )

    @pytest.fixture
    def sample_price(self):
        """Create sample price."""
        return Decimal("67000.50")

    @pytest.mark.asyncio
    async def test_execute_success(
        self,
        use_case,
        mock_fetch_and_save_use_case,
        mock_publish_use_case,
        sample_crypto_entity,
        sample_price,
    ):
        """Test successful execution of complete workflow."""
        # Arrange
        coin_id = "bitcoin"
        mock_fetch_and_save_use_case.execute.return_value = (
            sample_crypto_entity,
            sample_price,
        )

        # Act
        result_entity, result_price = await use_case.execute(coin_id)

        # Assert
        assert result_entity == sample_crypto_entity
        assert result_price == sample_price

        mock_fetch_and_save_use_case.execute.assert_called_once_with(coin_id=coin_id)
        mock_publish_use_case.execute.assert_called_once_with(
            cryptocurrency_id=sample_crypto_entity.id, new_price=sample_price
        )

    @pytest.mark.asyncio
    async def test_execute_fetch_fails(
        self, use_case, mock_fetch_and_save_use_case, mock_publish_use_case
    ):
        """Test when fetching from CoinGecko fails."""
        # Arrange
        coin_id = "bitcoin"
        mock_fetch_and_save_use_case.execute.side_effect = UnsuccessfullyCoinGeckoAPICall(
            "API error"
        )

        # Act & Assert
        with pytest.raises(UnsuccessfullyCoinGeckoAPICall):
            await use_case.execute(coin_id)

        # Publish should not be called
        mock_publish_use_case.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_repository_error(
        self, use_case, mock_fetch_and_save_use_case, mock_publish_use_case
    ):
        """Test when saving to database fails."""
        # Arrange
        coin_id = "bitcoin"
        mock_fetch_and_save_use_case.execute.side_effect = RepositoryError("Database error")

        # Act & Assert
        with pytest.raises(RepositoryError):
            await use_case.execute(coin_id)

        # Publish should not be called
        mock_publish_use_case.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_publish_fails(
        self,
        use_case,
        mock_fetch_and_save_use_case,
        mock_publish_use_case,
        sample_crypto_entity,
        sample_price,
    ):
        """Test when publishing to Kafka fails."""
        # Arrange
        coin_id = "bitcoin"
        mock_fetch_and_save_use_case.execute.return_value = (
            sample_crypto_entity,
            sample_price,
        )
        mock_publish_use_case.execute.side_effect = PublishError("Kafka error")

        # Act & Assert
        with pytest.raises(PublishError):
            await use_case.execute(coin_id)

        # Fetch should be called but publish fails
        mock_fetch_and_save_use_case.execute.assert_called_once()
        mock_publish_use_case.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_unexpected_error(
        self, use_case, mock_fetch_and_save_use_case, mock_publish_use_case
    ):
        """Test when unexpected error occurs."""
        # Arrange
        coin_id = "bitcoin"
        mock_fetch_and_save_use_case.execute.side_effect = ValueError("Unexpected error")

        # Act & Assert
        with pytest.raises(UnexpectedError):
            await use_case.execute(coin_id)

        mock_publish_use_case.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_with_different_coins(
        self, use_case, mock_fetch_and_save_use_case, mock_publish_use_case
    ):
        """Test execution with different coin IDs."""
        # Arrange
        coins = ["bitcoin", "ethereum", "cardano"]

        for coin_id in coins:
            entity = CryptocurrencyEntity(
                id=uuid4(),
                symbol=coin_id.upper()[:3],
                name=coin_id.capitalize(),
                coingecko_id=coin_id,
            )
            price = Decimal("1000.00")

            mock_fetch_and_save_use_case.execute.return_value = (entity, price)

            # Act
            result_entity, result_price = await use_case.execute(coin_id)

            # Assert
            assert result_entity.symbol == coin_id.upper()[:3]
            assert result_price == price

    @pytest.mark.asyncio
    async def test_execute_with_zero_price(
        self,
        use_case,
        mock_fetch_and_save_use_case,
        mock_publish_use_case,
        sample_crypto_entity,
    ):
        """Test execution with zero price."""
        # Arrange
        coin_id = "bitcoin"
        zero_price = Decimal("0.00")
        mock_fetch_and_save_use_case.execute.return_value = (
            sample_crypto_entity,
            zero_price,
        )

        # Act
        result_entity, result_price = await use_case.execute(coin_id)

        # Assert
        assert result_price == zero_price
        mock_publish_use_case.execute.assert_called_once_with(
            cryptocurrency_id=sample_crypto_entity.id, new_price=zero_price
        )

    @pytest.mark.asyncio
    async def test_execute_with_high_precision_price(
        self,
        use_case,
        mock_fetch_and_save_use_case,
        mock_publish_use_case,
        sample_crypto_entity,
    ):
        """Test execution with high precision decimal price."""
        # Arrange
        coin_id = "bitcoin"
        precise_price = Decimal("67123.456789")
        mock_fetch_and_save_use_case.execute.return_value = (
            sample_crypto_entity,
            precise_price,
        )

        # Act
        result_entity, result_price = await use_case.execute(coin_id)

        # Assert
        assert result_price == precise_price
        mock_publish_use_case.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_calls_in_correct_order(
        self,
        use_case,
        mock_fetch_and_save_use_case,
        mock_publish_use_case,
        sample_crypto_entity,
        sample_price,
    ):
        """Test that fetch and publish are called in correct order."""
        # Arrange
        coin_id = "bitcoin"
        call_order = []

        async def fetch_side_effect(*args, **kwargs):
            call_order.append("fetch")
            return (sample_crypto_entity, sample_price)

        async def publish_side_effect(*args, **kwargs):
            call_order.append("publish")

        mock_fetch_and_save_use_case.execute.side_effect = fetch_side_effect
        mock_publish_use_case.execute.side_effect = publish_side_effect

        # Act
        await use_case.execute(coin_id)

        # Assert
        assert call_order == ["fetch", "publish"]

    @pytest.mark.asyncio
    async def test_execute_returns_correct_types(
        self,
        use_case,
        mock_fetch_and_save_use_case,
        mock_publish_use_case,
        sample_crypto_entity,
        sample_price,
    ):
        """Test that execute returns correct types."""
        # Arrange
        coin_id = "bitcoin"
        mock_fetch_and_save_use_case.execute.return_value = (
            sample_crypto_entity,
            sample_price,
        )

        # Act
        result_entity, result_price = await use_case.execute(coin_id)

        # Assert
        assert isinstance(result_entity, CryptocurrencyEntity)
        assert isinstance(result_price, Decimal)

    @pytest.mark.asyncio
    async def test_execute_multiple_sequential_calls(
        self,
        use_case,
        mock_fetch_and_save_use_case,
        mock_publish_use_case,
        sample_crypto_entity,
        sample_price,
    ):
        """Test multiple sequential executions."""
        # Arrange
        coin_id = "bitcoin"
        mock_fetch_and_save_use_case.execute.return_value = (
            sample_crypto_entity,
            sample_price,
        )

        # Act
        for _ in range(3):
            result_entity, result_price = await use_case.execute(coin_id)

            # Assert
            assert result_entity == sample_crypto_entity
            assert result_price == sample_price

        # Verify called 3 times
        assert mock_fetch_and_save_use_case.execute.call_count == 3
        assert mock_publish_use_case.execute.call_count == 3
