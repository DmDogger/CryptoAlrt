"""Use case for processing cryptocurrency price updates.

Orchestrates the complete workflow: fetching price from API, saving to database,
publishing event to Kafka, and checking alert triggers.
"""

import structlog
from decimal import Decimal

from application.use_cases.fetch_and_save_to_database import FetchAndSaveUseCase
from application.use_cases.publish_price_update_to_broker import (
    PublishPriceUpdateToBrokerUseCase,
)
from application.use_cases.check_threshold import CheckThresholdUseCase
from domain.entities.cryptocurrency import CryptocurrencyEntity
from domain.exceptions import (
    UnsuccessfullyCoinGeckoAPICall,
    RepositoryError,
    PublishError,
    UnexpectedError,
)

logger = structlog.getLogger(__name__)


class ProcessPriceUpdateUseCase:
    """Use case for processing complete price update workflow.

    This use case orchestrates the full process of:
    1. Fetching price from CoinGecko API
    2. Saving price to database
    3. Publishing price update event to message broker
    4. Checking alert thresholds and sending notifications

    Attributes:
        _fetch_and_save_use_case: Use case for fetching and saving prices.
        _publish_price_updated_use_case: Use case for publishing price updates.
        _check_threshold_use_case: Use case for checking alert thresholds.
    """

    def __init__(
        self,
        fetch_and_save_use_case: FetchAndSaveUseCase,
        publish_price_updated_use_case: PublishPriceUpdateToBrokerUseCase,
        check_threshold_use_case: CheckThresholdUseCase,
    ):
        """Initialize the use case with required dependencies.

        Args:
            fetch_and_save_use_case: Use case for fetching and saving cryptocurrency prices.
            publish_price_updated_use_case: Use case for publishing price update events.
            check_threshold_use_case: Use case for checking alert thresholds.
        """
        self._fetch_and_save_use_case = fetch_and_save_use_case
        self._publish_price_updated_use_case = publish_price_updated_use_case
        self._check_threshold_use_case = check_threshold_use_case

    async def execute(
        self,
        coin_id: str,
    ) -> tuple[CryptocurrencyEntity, Decimal]:
        """Execute the complete price update workflow.

        This method:
        1. Fetches current price from CoinGecko API
        2. Saves price to database
        3. Publishes price update event to Kafka broker
        4. Checks alert thresholds and sends notifications

        Args:
            coin_id: CoinGecko coin identifier (e.g., "bitcoin", "ethereum").

        Returns:
            tuple: (CryptocurrencyEntity, current_price) - saved entity and its price.

        Raises:
            UnsuccessfullyCoinGeckoAPICall: If fetching from CoinGecko API fails.
            RepositoryError: If saving to database fails.
            PublishError: If publishing to Kafka fails.
            UnexpectedError: If any unexpected error occurs.

        """
        try:
            logger.debug(
                "Starting price update workflow",
                coin_id=coin_id,
            )

            logger.info("Fetching price from CoinGecko and saving to database")
            crypto_entity, current_price = await self._fetch_and_save_use_case.execute(
                coin_id=coin_id
            )
            logger.info(
                "Successfully fetched and saved",
                symbol=crypto_entity.symbol,
                crypto_id=crypto_entity.id,
                curr_price=current_price,
            )

            logger.info("Publishing price update event to Kafka")
            await self._publish_price_updated_use_case.execute(
                cryptocurrency_id=crypto_entity.id, new_price=current_price
            )
            logger.info("Successfully published price update to Kafka")

            await self._check_threshold_use_case.execute(
                cryptocurrency=crypto_entity.symbol, current_price=current_price
            )
            logger.info(
                "Successfully checked thresholds",
                symbol=crypto_entity.symbol,
            )

            return crypto_entity, current_price

        except UnsuccessfullyCoinGeckoAPICall as e:
            logger.error(
                "Failed to fetch price from CoinGecko",
                coint_id=coin_id,
                error=str(e),
                exc_info=True,
                error_type=type(e).__name__,
            )
            raise

        except RepositoryError as e:
            logger.error(
                "Failed to save fetched prices to database",
                coint_id=coin_id,
                error=str(e),
                exc_info=True,
                error_type=type(e).__name__,
            )
            raise

        except PublishError as e:
            logger.error(
                "Failed to publish message into broker",
                coint_id=coin_id,
                error=str(e),
                exc_info=True,
                error_type=type(e).__name__,
            )
            raise

        except Exception as e:
            logger.error(
                "Unexpected error occurred",
                error=str(e),
                exc_info=True,
            )
            raise UnexpectedError(
                f"Unexpected error during price update for {coin_id}: {str(e)}"
            ) from e
