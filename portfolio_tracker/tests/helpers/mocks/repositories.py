import pytest
import pytest_asyncio
from infrastructures.database.repositories.cached_portfolio_repository import (
    CachedPortfolioRepository,
)

from application.interfaces import PortfolioRepositoryProtocol
from helpers.fakes.fake_portfolio_repository import FakePortfolioRepository
from infrastructures.cache.redis import RedisCache
from infrastructures.database.mappers.portfolio_db_mapper import PortfolioDBMapper


@pytest.fixture
def fake_portfolio_repository():
    return FakePortfolioRepository()


@pytest_asyncio.fixture
async def mock_cached_portfolio_repository(mock_redis_client, fake_portfolio_repository):
    return CachedPortfolioRepository(
        _redis_client=RedisCache(client=mock_redis_client),
        _original=fake_portfolio_repository,
        _mapper=PortfolioDBMapper(),
    )
