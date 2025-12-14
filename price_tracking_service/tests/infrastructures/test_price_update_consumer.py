import sys
import pytest
from datetime import datetime, UTC
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

# Mock faststream.kafka before importing consumer
mock_kafka = MagicMock()
sys.modules['faststream.kafka'] = mock_kafka

from src.infrastructures.consumer.price_update_consumer import _consume_price_update_and_check_thresholds
from src.domain.events.price_updated import PriceUpdatedEvent
from src.domain.exceptions import RepositoryError, PublishError


class TestConsumePriceUpdateAndCheckThresholds:
    """Tests for consume_price_update_and_check_thresholds consumer function."""

    @pytest.fixture
    def mock_use_case(self):
        """Create mock CheckThresholdUseCase."""
        use_case = MagicMock()
        use_case.execute = AsyncMock()
        return use_case

    @pytest.fixture
    def price_updated_event(self):
        """Create sample PriceUpdatedEvent."""
        return PriceUpdatedEvent(
            id=uuid4(),
            cryptocurrency="bitcoin",
            name="Bitcoin",
            price=Decimal("67000.50"),
            timestamp=datetime.now(UTC)
        )

    @pytest.mark.asyncio
    async def test_consume_success(self, mock_use_case, price_updated_event, caplog):
        """Test successful consumption and processing of price update event."""
        # Arrange
        with patch('src.infrastructures.consumer.price_update_consumer.logger') as mock_logger:
            # Act
            await _consume_price_update_and_check_thresholds(
                event=price_updated_event,
                use_case=mock_use_case
            )

            # Assert
            mock_use_case.execute.assert_called_once_with(
                cryptocurrency=price_updated_event.cryptocurrency,
                current_price=price_updated_event.price
            )

            # Verify logging
            mock_logger.info.assert_any_call(
                "[Consumer] Received price update message",
                cryptocurrency=price_updated_event.cryptocurrency,
                current_price=str(price_updated_event.price),
                topic="price-updates"
            )

            mock_logger.debug.assert_called_once_with(
                "[Consumer] Starting threshold check use case execution",
                cryptocurrency=price_updated_event.cryptocurrency,
                current_price=str(price_updated_event.price)
            )

            mock_logger.info.assert_any_call(
                "[Consumer] Successfully processed price update and checked thresholds",
                cryptocurrency=price_updated_event.cryptocurrency,
                current_price=str(price_updated_event.price)
            )

    @pytest.mark.asyncio
    async def test_consume_repository_error(self, mock_use_case, price_updated_event, caplog):
        """Test handling of RepositoryError during consumption."""
        # Arrange
        repo_error = RepositoryError("Database connection failed")
        mock_use_case.execute.side_effect = repo_error

        with patch('src.infrastructures.consumer.price_update_consumer.logger') as mock_logger:
            # Act
            await _consume_price_update_and_check_thresholds(
                event=price_updated_event,
                use_case=mock_use_case
            )

            # Assert
            mock_use_case.execute.assert_called_once_with(
                cryptocurrency=price_updated_event.cryptocurrency,
                current_price=price_updated_event.price
            )

            # Verify error logging
            mock_logger.error.assert_called_once_with(
                "[Consumer] Database repository error occurred while processing price update",
                error=str(repo_error),
                error_type="RepositoryError",
                cryptocurrency=price_updated_event.cryptocurrency,
                current_price=str(price_updated_event.price),
                topic="price-updates",
                exc_info=True
            )

    @pytest.mark.asyncio
    async def test_consume_publish_error(self, mock_use_case, price_updated_event, caplog):
        """Test handling of PublishError during consumption."""
        # Arrange
        publish_error = PublishError("Failed to publish alert event")
        mock_use_case.execute.side_effect = publish_error

        with patch('src.infrastructures.consumer.price_update_consumer.logger') as mock_logger:
            # Act
            await _consume_price_update_and_check_thresholds(
                event=price_updated_event,
                use_case=mock_use_case
            )

            # Assert
            mock_use_case.execute.assert_called_once_with(
                cryptocurrency=price_updated_event.cryptocurrency,
                current_price=price_updated_event.price
            )

            # Verify error logging
            mock_logger.error.assert_called_once_with(
                "[Consumer] Message publishing error occurred while processing price update",
                error=str(publish_error),
                error_type="PublishError",
                cryptocurrency=price_updated_event.cryptocurrency,
                current_price=str(price_updated_event.price),
                topic="price-updates",
                exc_info=True
            )

    @pytest.mark.asyncio
    async def test_consume_value_error(self, mock_use_case, price_updated_event, caplog):
        """Test handling of ValueError during consumption."""
        # Arrange
        value_error = ValueError("Invalid price format")
        mock_use_case.execute.side_effect = value_error

        with patch('src.infrastructures.consumer.price_update_consumer.logger') as mock_logger:
            # Act
            await _consume_price_update_and_check_thresholds(
                event=price_updated_event,
                use_case=mock_use_case
            )

            # Assert
            mock_use_case.execute.assert_called_once_with(
                cryptocurrency=price_updated_event.cryptocurrency,
                current_price=price_updated_event.price
            )

            # Verify error logging
            mock_logger.error.assert_called_once_with(
                "[Consumer] Invalid data format received in price update message",
                error=str(value_error),
                error_type="ValueError",
                cryptocurrency=price_updated_event.cryptocurrency,
                current_price=str(price_updated_event.price),
                topic="price-updates",
                exc_info=True
            )

    @pytest.mark.asyncio
    async def test_consume_unexpected_error(self, mock_use_case, price_updated_event, caplog):
        """Test handling of unexpected errors during consumption."""
        # Arrange
        unexpected_error = RuntimeError("Unexpected system error")
        mock_use_case.execute.side_effect = unexpected_error

        with patch('src.infrastructures.consumer.price_update_consumer.logger') as mock_logger:
            # Act
            await _consume_price_update_and_check_thresholds(
                event=price_updated_event,
                use_case=mock_use_case
            )

            # Assert
            mock_use_case.execute.assert_called_once_with(
                cryptocurrency=price_updated_event.cryptocurrency,
                current_price=price_updated_event.price
            )

            # Verify critical error logging
            mock_logger.critical.assert_called_once_with(
                "[Consumer] Unexpected error occurred while processing price update",
                error=str(unexpected_error),
                error_type="RuntimeError",
                cryptocurrency=price_updated_event.cryptocurrency,
                current_price=str(price_updated_event.price),
                topic="price-updates",
                exc_info=True
            )

    @pytest.mark.asyncio
    async def test_consume_with_different_cryptocurrencies(self, mock_use_case, caplog):
        """Test consumption with different cryptocurrency events."""
        # Arrange
        cryptocurrencies = ["bitcoin", "ethereum", "cardano", "solana"]

        with patch('src.infrastructures.consumer.price_update_consumer.logger') as mock_logger:
            for crypto in cryptocurrencies:
                event = PriceUpdatedEvent(
                    id=uuid4(),
                    cryptocurrency=crypto,
                    name=crypto.capitalize(),
                    price=Decimal("1000.00"),
                    timestamp=datetime.now(UTC)
                )

                # Act
                await _consume_price_update_and_check_thresholds(
                    event=event,
                    use_case=mock_use_case
                )

                # Assert
                mock_use_case.execute.assert_called_with(
                    cryptocurrency=crypto,
                    current_price=Decimal("1000.00")
                )

    @pytest.mark.asyncio
    async def test_consume_with_different_prices(self, mock_use_case, caplog):
        """Test consumption with different price values."""
        # Arrange
        prices = [Decimal("0.01"), Decimal("1.50"), Decimal("1000000.99"), Decimal("999999.999999")]

        with patch('src.infrastructures.consumer.price_update_consumer.logger') as mock_logger:
            for price in prices:
                event = PriceUpdatedEvent(
                    id=uuid4(),
                    cryptocurrency="bitcoin",
                    name="Bitcoin",
                    price=price,
                    timestamp=datetime.now(UTC)
                )

                # Act
                await _consume_price_update_and_check_thresholds(
                    event=event,
                    use_case=mock_use_case
                )

                # Assert
                mock_use_case.execute.assert_called_with(
                    cryptocurrency="bitcoin",
                    current_price=price
                )

    @pytest.mark.asyncio
    async def test_consume_no_exceptions_raised(self, mock_use_case, price_updated_event):
        """Test that consumer function never raises exceptions."""
        # Arrange
        mock_use_case.execute.side_effect = Exception("Any error")

        # Act & Assert
        # Function should not raise any exceptions
        await _consume_price_update_and_check_thresholds(
            event=price_updated_event,
            use_case=mock_use_case
        )

    @pytest.mark.asyncio
    async def test_consume_logging_context(self, mock_use_case, price_updated_event):
        """Test that all log messages include proper context."""
        # Arrange
        with patch('src.infrastructures.consumer.price_update_consumer.logger') as mock_logger:
            # Act
            await _consume_price_update_and_check_thresholds(
                event=price_updated_event,
                use_case=mock_use_case
            )

            # Assert
            # Check that all info logs include cryptocurrency and price
            info_calls = mock_logger.info.call_args_list
            assert len(info_calls) == 2  # Received and Success messages

            for call in info_calls:
                args, kwargs = call
                assert "cryptocurrency" in kwargs
                assert "current_price" in kwargs
                assert kwargs["cryptocurrency"] == price_updated_event.cryptocurrency
                assert kwargs["current_price"] == str(price_updated_event.price)

    @pytest.mark.asyncio
    async def test_consume_error_logging_includes_topic(self, mock_use_case, price_updated_event):
        """Test that error logs include topic information."""
        # Arrange
        mock_use_case.execute.side_effect = RepositoryError("Test error")

        with patch('src.infrastructures.consumer.price_update_consumer.logger') as mock_logger:
            # Act
            await _consume_price_update_and_check_thresholds(
                event=price_updated_event,
                use_case=mock_use_case
            )

            # Assert
            error_call = mock_logger.error.call_args
            args, kwargs = error_call
            assert "topic" in kwargs
            assert kwargs["topic"] == "price-updates"