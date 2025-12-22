import structlog
from typing import final

from application.interfaces.repositories import CryptocurrencyRepositoryProtocol
from domain.exceptions import RepositoryError

logger = structlog.getLogger(__name__)


@final
class GetCryptocurrenciesWithPricesUseCase:
    """Use case for retrieving all cryptocurrencies with their latest prices.
    
    This use case fetches all cryptocurrencies from the database along with
    their most recent price information.
    """

    def __init__(
        self,
        cryptocurrency_repository: CryptocurrencyRepositoryProtocol,
    ):
        """Initialize the use case with required repository.
        
        Args:
            cryptocurrency_repository: Repository for accessing cryptocurrency data.
        """
        self._repository = cryptocurrency_repository

    async def execute(self) -> list:
        """Execute the retrieval of cryptocurrencies with prices.
        
        Returns:
            List of dictionaries containing cryptocurrency data with latest prices.
            
        Raises:
            RepositoryError: If database operation fails.
        """
        try:
            logger.info("Fetching cryptocurrencies with prices")
            
            cryptocurrencies = await self._repository.get_sorted_cryptocurrencies_by_created_at_time()
            
            result = []
            for crypto in cryptocurrencies:
                # Get latest price for each cryptocurrency
                latest_price = await self._repository.get_last_price(crypto.id)
                
                # Get latest price details (24h high/low, volume, etc.)
                # TODO: Add method to get full price details if needed
                
                result.append({
                    "id": str(crypto.id),
                    "coingecko_id": crypto.coingecko_id,
                    "symbol": crypto.symbol,
                    "name": crypto.name,
                    "price": float(latest_price) if latest_price else None,
                })
            
            logger.info(
                "Successfully retrieved cryptocurrencies with prices",
                count=len(result)
            )
            
            return result
            
        except RepositoryError as e:
            logger.error(
                "Repository error during cryptocurrency retrieval",
                error=str(e),
                exc_info=True
            )
            raise
        except Exception as e:
            logger.error(
                "Unexpected error during cryptocurrency retrieval",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )
            raise



