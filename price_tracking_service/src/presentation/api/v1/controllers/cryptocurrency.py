from dishka.integrations.fastapi import inject, FromDishka
from fastapi import APIRouter

from application.use_cases.get_cryptocurrencies_with_prices import GetCryptocurrenciesWithPricesUseCase
from presentation.api.v1.schemas.cryptocurrency import CryptocurrencyPriceResponse

router = APIRouter(prefix="/cryptocurrencies")


@router.get("/v1/", response_model=list[CryptocurrencyPriceResponse], status_code=200)
@inject
async def get_cryptocurrencies_with_prices(
    use_case: FromDishka[GetCryptocurrenciesWithPricesUseCase],
) -> list[CryptocurrencyPriceResponse]:
    """Get all cryptocurrencies with their latest prices."""
    data = await use_case.execute()
    return [CryptocurrencyPriceResponse(**item) for item in data]





