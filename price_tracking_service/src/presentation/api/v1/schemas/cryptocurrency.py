from pydantic import BaseModel


class CryptocurrencyPriceResponse(BaseModel):
    """Response schema for cryptocurrency with price data."""
    id: str
    coingecko_id: str
    symbol: str
    name: str
    price: float | None


class CryptocurrenciesListResponse(BaseModel):
    """Response schema for list of cryptocurrencies."""
    cryptocurrencies: list[CryptocurrencyPriceResponse]





