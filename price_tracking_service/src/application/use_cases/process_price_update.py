import structlog
from decimal import Decimal

from src.application.use_cases.fetch_and_save_to_database import FetchAndSaveUseCase
from src.application.use_cases.publish_price_update_to_broker import PublishPriceUpdateToBrokerUseCase
from src.domain.entities.cryptocurrency import CryptocurrencyEntity
from src.domain.exceptions import (
    UnsuccessfullyCoinGeckoAPICall,
    RepositoryError,
    PublishError,
    UnexpectedError
)

logger = structlog.getLogger(__name__)


class ProcessPriceUpdateUseCase:
    """Use case for processing complete price update workflow.
    
    This use case orchestrates the full process of:
    1. Fetching price from CoinGecko API
    2. Saving price to database
    3. Publishing price update event to message broker
    
    Attributes:
        _fetch_and_save_use_case: Use case for fetching and saving prices.
        _publish_price_updated_use_case: Use case for publishing price updates.
    """
    
    def __init__(
            self,
            fetch_and_save_use_case: FetchAndSaveUseCase,
            publish_price_updated_use_case: PublishPriceUpdateToBrokerUseCase,
    ):
        """Initialize the use case with required dependencies.
        
        Args:
            fetch_and_save_use_case: Use case for fetching and saving cryptocurrency prices.
            publish_price_updated_use_case: Use case for publishing price update events.
        """
        self._fetch_and_save_use_case = fetch_and_save_use_case
        self._publish_price_updated_use_case = publish_price_updated_use_case

    async def execute(
            self,
            coin_id: str,
    ) -> tuple[CryptocurrencyEntity, Decimal]:
        """Execute the complete price update workflow.
        
        This method:
        1. Fetches current price from CoinGecko API
        2. Saves price to database
        3. Publishes price update event to Kafka broker
        
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
            logger.info(f"[ProcessPriceUpdate]: Starting price update workflow for {coin_id}")
            

            logger.info(f"[Info]: Fetching price from CoinGecko and saving to database")
            crypto_entity, current_price = await self._fetch_and_save_use_case.execute(coin_id=coin_id)
            logger.info(
                f"[Info]: Successfully fetched and saved {crypto_entity.symbol} "
                f"(ID: {crypto_entity.id}) at ${current_price} USD"
            )

            logger.info(f"[Step 2/2]: Publishing price update event to Kafka")
            await self._publish_price_updated_use_case.execute(
                cryptocurrency_id=crypto_entity.id,
                new_price=current_price
            )
            logger.info(f"[Info]: Successfully published price update to Kafka")
            
            logger.info(
                f"[ProcessPriceUpdate]: Complete workflow finished for {crypto_entity.symbol} "
                f"at ${current_price} USD"
            )
            
            return crypto_entity, current_price

        except UnsuccessfullyCoinGeckoAPICall as e:
            logger.error(
                f"[ProcessPriceUpdate]: Failed to fetch price from CoinGecko for {coin_id}: {e}"
            )
            raise

        except RepositoryError as e:
            logger.error(
                f"[ProcessPriceUpdate]: Failed to save price to database for {coin_id}: {e}"
            )
            raise

        except PublishError as e:
            logger.error(
                f"[ProcessPriceUpdate]: Failed to publish price update to Kafka for {coin_id}: {e}"
            )
            raise

        except Exception as e:
            logger.error(
                f"[ProcessPriceUpdate]: Unexpected error during price update workflow for {coin_id}: {e}",
                exc_info=True
            )
            raise UnexpectedError(f"Unexpected error during price update for {coin_id}: {str(e)}") from e


