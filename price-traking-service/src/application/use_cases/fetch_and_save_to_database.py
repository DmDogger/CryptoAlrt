import structlog

from src.application.interfaces.coingecko_client import CoinGeckoClientProtocol
from src.application.interfaces.repositories import CryptocurrencyRepositoryProtocol
from src.domain.entities.cryptocurrency import CryptocurrencyEntity
from src.domain.exceptions import UnsuccessfullyCoinGeckoAPICall, UnexpectedError

logger = structlog.getLogger(__name__)

class FetchAndSaveUseCase:
    """Use case for fetching cryptocurrency price from CoinGecko API and saving to database.
    
    This use case orchestrates the following operations:
    1. Fetch price data from CoinGecko API
    2. Get or create cryptocurrency entity
    3. Save price data to database
    
    Attributes:
        _coingecko_client: Client for interacting with CoinGecko API.
        _crypto_repository: Repository for cryptocurrency persistence.
    """
    
    def __init__(
            self,
            coingecko_client: CoinGeckoClientProtocol,
            crypto_repository: CryptocurrencyRepositoryProtocol
    ):
        """Initialize the use case with required dependencies.
        
        Args:
            coingecko_client: Client for fetching data from CoinGecko API.
            crypto_repository: Repository for cryptocurrency operations.
        """
        self._coingecko_client = coingecko_client
        self._crypto_repository = crypto_repository

    async def execute(
            self,
            coin_id: str
    ) -> CryptocurrencyEntity:
        """Execute the use case to fetch and save cryptocurrency price.
        
        This method:
        1. Fetches price data from CoinGecko API using coin_id
        2. Checks if cryptocurrency exists in database by symbol
        3. Creates new cryptocurrency entity if not found
        4. Saves price data associated with the cryptocurrency
        
        Args:
            coin_id: CoinGecko coin identifier (e.g., "bitcoin", "ethereum").
        
        Raises:
            UnsuccessfullyCoinGeckoAPICall: If API request fails or returns None.
            UnexpectedError: If any unexpected error occurs during execution.

        """
        try:
            logger.info(f"[Info]: Preparing to fetch with coin_id: {coin_id}")
            coingecko_dto = await self._coingecko_client.fetch_price(coin_id)

            if coingecko_dto is None:
                logger.error(f"[Error]: Unsuccessfully fetching. Coingecko returned None.")
                raise UnsuccessfullyCoinGeckoAPICall(f"[Error]: Unsuccessfully fetching. Coingecko returned None.")

            crypto_entity = await self._crypto_repository.get_cryptocurrency_by_symbol(coingecko_dto.symbol)
            
            if crypto_entity is None:
                logger.info(f"[Info]: Cryptocurrency with symbol {coingecko_dto.symbol} not found, creating new one")
                crypto_entity = CryptocurrencyEntity(
                    symbol=coingecko_dto.symbol,
                    name=coingecko_dto.name
                )
                await self._crypto_repository.save(crypto_entity)
                logger.info(f"[Success]: Created cryptocurrency {crypto_entity.id}")

            logger.info(f"[Info]: Preparing to save price to database...")
            crypto_entity = await self._crypto_repository.save_price(
                cryptocurrency_id=crypto_entity.id,
                price_data=coingecko_dto
            )
            logger.info(f"[Success]: Price successfully saved for {coingecko_dto.symbol}")

            return crypto_entity, coingecko_dto.current_price

        except UnsuccessfullyCoinGeckoAPICall:
            raise
        except Exception as e:
            logger.error(f"[Unexpected error]: Occurred unexpected error: {e}")
            raise UnexpectedError(f"Occurred unexpected error")

