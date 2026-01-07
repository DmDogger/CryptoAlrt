from dataclasses import dataclass
from typing import final

import httpx
import stamina
import structlog

from application.dtos.coingecko_object import CoinGeckoDTO
from application.interfaces.coingecko_client import CoinGeckoClientProtocol
from application.interfaces.repositories import CryptocurrencyRepositoryProtocol
from config.coingecko import coingecko_settings
from domain.exceptions import UnsuccessfullyCoinGeckoAPICall, CryptocurrencyNotFound

logger = structlog.getLogger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CoinGeckoClient(CoinGeckoClientProtocol):
    """HTTP client for fetching cryptocurrency prices from CoinGecko API.

    Uses httpx for async HTTP requests with stamina retry logic.
    Implements CoinGeckoClientProtocol interface.

    Attributes:
        client: Async HTTP client for making requests to CoinGecko API.
        cryptocurrency_repository: Repository for cryptocurrency data operations.
    """

    client: httpx.AsyncClient
    cryptocurrency_repository: CryptocurrencyRepositoryProtocol

    @stamina.retry(
        on=(httpx.HTTPStatusError, httpx.RequestError, KeyError),
        attempts=3,
    )
    async def fetch_price(self, coin_id: str) -> CoinGeckoDTO | None:
        """Fetch current price data for a cryptocurrency from CoinGecko API.

        Makes a request to /simple/price endpoint with retry logic (3 attempts).
        Returns price data including current price, market cap, 24h volume, etc.

        Args:
            coin_id: CoinGecko coin identifier (e.g., "bitcoin", "ethereum").

        Returns:
            CoinGeckoDTO with price data if successful, None if coin not found.

        Raises:
            UnsuccessfullyCoinGeckoAPICall: If API request fails after retries.
            CryptocurrencyNotFound: If coin_id doesn't exist in CoinGecko.
        """
        try:
            url = f"{coingecko_settings.base_url}coins/markets"
            params = {
                "vs_currency": "usd",
                "ids": coin_id,
                "order": "market_cap_desc",
                "per_page": 1,
                "page": 1,
                "sparkline": "false",
                "price_change_percentage": "24h",
            }

            logger.info(
                f"[Info]: Preparing to fetch from CoinGecko with url: {url}, coin_id: {coin_id}"
            )

            response = await self.client.get(
                url=url, headers=coingecko_settings.headers, params=params
            )

            response.raise_for_status()
            data = response.json()

            if not data or len(data) == 0:
                raise CryptocurrencyNotFound(f"Coin '{coin_id}' not found in CoinGecko")

            logger.info(
                f"[Info]: Successfully fetched information from CoinGecko for coin_id: {coin_id}"
            )
            return CoinGeckoDTO.to_dto(data[0])

        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            logger.exception(
                f"[HTTP Error]: Error during fetching from CoinGecko: {e} for coin_id '{coin_id}' with URL: {url}"
            )
            raise UnsuccessfullyCoinGeckoAPICall(
                f"Error occurred during fetching from CoinGecko API: {e}"
            )

        except KeyError as e:
            logger.exception(f"[KeyError]: CoinGecko returned invalid data: {e}")
            raise UnsuccessfullyCoinGeckoAPICall(
                f"Error occurred during fetching from CoinGecko API: {e}"
            )
        except Exception as e:
            logger.exception(f"[Unexpected error]: Occurred unexpected error: {e}")
            raise UnsuccessfullyCoinGeckoAPICall(
                f"Error occurred during fetching from CoinGecko API: {e}"
            )
