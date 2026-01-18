"""Fixtures for infrastructure layer tests."""

from datetime import datetime, UTC, timedelta
from decimal import Decimal
from typing import AsyncGenerator, Any

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from unittest.mock import AsyncMock, MagicMock

from infrastructures.database.models.portfolio import Portfolio
from infrastructures.database.models.asset import Asset
from infrastructures.database.models.cryptoprice import CryptoPrice
from infrastructures.database.mappers.portfolio_db_mapper import PortfolioDBMapper
from infrastructures.database.mappers.asset_db_mapper import AssetDBMapper
from infrastructures.database.repositories.portfolio import SQLAlchemyPortfolioRepository
from testcontainers.postgres import PostgresContainer

from infrastructures.database.repositories.cached_portfolio_repository import (
    CachedPortfolioRepository,
)

from infrastructures.cache.redis import RedisCache


@pytest.fixture
def mock_result_obj():
    """Mock Result object for testing query results."""
    result = MagicMock()
    result.first = MagicMock()
    result.all = MagicMock()
    result.scalar_one_or_none = MagicMock()
    result.scalars = MagicMock()
    result.one_or_none = MagicMock()
    result.scalar_one = MagicMock()
    result.unique = MagicMock(return_value=result)
    return result


@pytest.fixture
def mock_async_session(mock_result_obj):
    """Mock AsyncSession for testing repositories."""
    session = AsyncMock(spec=AsyncSession)
    session.scalars = AsyncMock()
    session.scalar_one = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.get = AsyncMock()
    session.execute = AsyncMock(return_value=mock_result_obj)
    session.add = MagicMock()
    return session


@pytest.fixture
def mock_portfolio_mapper():
    """Mock PortfolioDBMapper for testing repositories."""
    mapper = MagicMock(spec=PortfolioDBMapper)
    mapper.to_database = MagicMock()
    mapper.from_database = MagicMock()
    return mapper


@pytest.fixture
def mock_portfolio_repository(
    mock_async_session: AsyncMock,
    mock_portfolio_mapper: MagicMock,
) -> SQLAlchemyPortfolioRepository:
    """Real SQLAlchemyPortfolioRepository with mocked session for testing."""
    return SQLAlchemyPortfolioRepository(
        _session=mock_async_session,
        _mapper=mock_portfolio_mapper,
        _asset_mapper=AssetDBMapper(),
    )


@pytest.fixture
def sample_portfolio_db_model():
    """Fixture providing a sample Portfolio database model instance."""
    now = datetime.now(UTC).replace(tzinfo=None)
    return Portfolio(
        wallet_address="walletaddress4tests",
        total_value=Decimal("1000.00"),
        weight=Decimal("50.00"),
        portfolio_total=Decimal("2000.00"),
        updated_at=now,
        created_at=now,
    )


@pytest.fixture(scope="session")
def postgres_container():
    """PostgreSQL testcontainer for integration tests."""
    with PostgresContainer("postgres:16", driver=None) as container:
        yield container


@pytest_asyncio.fixture(scope="function")
async def async_session(postgres_container):
    """AsyncSession for SQLAlchemy using testcontainers PostgreSQL."""
    psql_url = postgres_container.get_connection_url()
    async_url = psql_url.replace("postgresql://", "postgresql+asyncpg://").replace(
        "postgres://", "postgresql+asyncpg://"
    )

    engine = create_async_engine(
        async_url,
        poolclass=NullPool,
        echo=False,
    )

    from infrastructures.database.models.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def portfolio_repository_for_transactions(async_session):
    """Real SQLAlchemyPortfolioRepository with real database session for transaction testing."""
    return SQLAlchemyPortfolioRepository(
        _session=async_session,
        _mapper=PortfolioDBMapper(),
        _asset_mapper=AssetDBMapper(),
    )


@pytest.fixture(scope="function")
async def fill_with_the_base_fields(sample_portfolio_entity, async_session):
    """Fixture that adds CryptoPrice and Asset to session (without commit).
    Commit should be done in test after Portfolio is saved.
    Data is rolled back after test."""
    from sqlalchemy import select

    ticker = sample_portfolio_entity.assets[0].ticker
    wallet_address = sample_portfolio_entity.wallet_address

    existing_crypto_price = await async_session.execute(
        select(CryptoPrice).where(CryptoPrice.cryptocurrency == ticker)
    )
    if existing_crypto_price.scalar_one_or_none() is None:
        crypto_price = CryptoPrice(
            cryptocurrency=ticker,
            price=Decimal("90000.00"),
            updated_at=datetime.now(UTC).replace(tzinfo=None),
        )
        async_session.add(crypto_price)

    existing_asset = await async_session.execute(
        select(Asset).where(Asset.wallet_address == wallet_address, Asset.ticker == ticker)
    )
    if existing_asset.scalar_one_or_none() is None:
        asset_model = AssetDBMapper.to_database(sample_portfolio_entity.assets[0])
        async_session.add(asset_model)

    yield

    await async_session.rollback()


@pytest.fixture(scope="function")
async def fill_integration_base_fields(integration_portfolio_entity, async_session):
    """Fixture for integration tests that adds CryptoPrice, Asset and MarketPriceHistory to session."""
    from sqlalchemy import select
    from infrastructures.database.models.cryptoprice import MarketPriceHistory

    ticker = integration_portfolio_entity.assets[0].ticker
    wallet_address = integration_portfolio_entity.wallet_address

    existing_crypto_price = await async_session.execute(
        select(CryptoPrice).where(CryptoPrice.cryptocurrency == ticker)
    )
    if existing_crypto_price.scalar_one_or_none() is None:
        crypto_price = CryptoPrice(
            cryptocurrency=ticker,
            price=Decimal("90000.00"),
            updated_at=datetime.now(UTC).replace(tzinfo=None),
        )
        async_session.add(crypto_price)

    existing_price_history = await async_session.execute(
        select(MarketPriceHistory).where(
            MarketPriceHistory.cryptocurrency == ticker,
            MarketPriceHistory.timestamp
            >= datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=24),
        )
    )
    if existing_price_history.scalar_one_or_none() is None:
        price_history = MarketPriceHistory(
            cryptocurrency=ticker,
            name="Bitcoin",
            price=Decimal("85000.00"),
            timestamp=datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=1),
        )
        async_session.add(price_history)

    # Assets will be created via cascade when portfolio is saved
    # No need to create them here to avoid duplicates

    yield

    await async_session.rollback()


@pytest_asyncio.fixture
async def fill_prices_only(integration_portfolio_entity, async_session):
    """Fixture for integration tests that adds only CryptoPrice and MarketPriceHistory (without Asset)."""
    from sqlalchemy import select
    from infrastructures.database.models.cryptoprice import MarketPriceHistory

    ticker = integration_portfolio_entity.assets[0].ticker

    existing_crypto_price = await async_session.execute(
        select(CryptoPrice).where(CryptoPrice.cryptocurrency == ticker)
    )
    if existing_crypto_price.scalar_one_or_none() is None:
        crypto_price = CryptoPrice(
            cryptocurrency=ticker,
            price=Decimal("90000.00"),
            updated_at=datetime.now(UTC).replace(tzinfo=None),
        )
        async_session.add(crypto_price)

    existing_price_history = await async_session.execute(
        select(MarketPriceHistory).where(
            MarketPriceHistory.cryptocurrency == ticker,
            MarketPriceHistory.timestamp
            >= datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=24),
        )
    )
    if existing_price_history.scalar_one_or_none() is None:
        price_history = MarketPriceHistory(
            cryptocurrency=ticker,
            name="Bitcoin",
            price=Decimal("85000.00"),
            timestamp=datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=1),
        )
        async_session.add(price_history)

    yield

    await async_session.rollback()


@pytest_asyncio.fixture
async def fill_eth_price(async_session):
    """Fixture that adds CryptoPrice for ETH ticker."""
    from sqlalchemy import select

    existing_eth_price = await async_session.execute(
        select(CryptoPrice).where(CryptoPrice.cryptocurrency == "ETH")
    )
    if existing_eth_price.scalar_one_or_none() is None:
        eth_price = CryptoPrice(
            cryptocurrency="ETH",
            price=Decimal("3000.00"),
            updated_at=datetime.now(UTC).replace(tzinfo=None),
        )
        async_session.add(eth_price)

    yield

    await async_session.rollback()


@pytest_asyncio.fixture
async def fill_btc_eth_prices(async_session):
    """Fixture that adds CryptoPrice for BTC and ETH tickers."""
    from sqlalchemy import select

    for ticker in ["BTC", "ETH"]:
        existing = await async_session.execute(
            select(CryptoPrice).where(CryptoPrice.cryptocurrency == ticker)
        )
        if existing.scalar_one_or_none() is None:
            crypto_price = CryptoPrice(
                cryptocurrency=ticker,
                price=Decimal("90000.00") if ticker == "BTC" else Decimal("3000.00"),
                updated_at=datetime.now(UTC).replace(tzinfo=None),
            )
            async_session.add(crypto_price)
    await async_session.commit()

    yield

    await async_session.rollback()


@pytest.fixture(scope="function")
def add_asset_and_crypto_price_for_portfolio(integration_portfolio_entity, async_session):
    """Fixture that returns a function to add CryptoPrice and Asset to session."""
    from sqlalchemy import select

    async def _add_data():
        ticker = integration_portfolio_entity.assets[0].ticker
        wallet_address = integration_portfolio_entity.wallet_address

        existing_crypto_price = await async_session.execute(
            select(CryptoPrice).where(CryptoPrice.cryptocurrency == ticker)
        )
        if existing_crypto_price.scalar_one_or_none() is None:
            crypto_price = CryptoPrice(
                cryptocurrency=ticker,
                price=Decimal("90000.00"),
                updated_at=datetime.now(UTC).replace(tzinfo=None),
            )
            async_session.add(crypto_price)

        existing_asset = await async_session.execute(
            select(Asset).where(Asset.wallet_address == wallet_address, Asset.ticker == ticker)
        )
        if existing_asset.scalar_one_or_none() is None:
            asset_model = AssetDBMapper.to_database(integration_portfolio_entity.assets[0])
            async_session.add(asset_model)

    return _add_data


@pytest.fixture
def sample_crypto_price_db_model():
    """Fixture providing a sample CryptoPrice database model instance."""
    return CryptoPrice(
        cryptocurrency="BTC",
        price=Decimal("90000.00"),
        updated_at=datetime.now(UTC).replace(tzinfo=None),
    )


@pytest.fixture
def sample_asset_db_model(sample_uuid, sample_crypto_price_db_model):
    """Fixture providing a sample Asset database model instance."""
    return Asset(
        asset_id=sample_uuid,
        ticker="BTC",
        amount=Decimal("0.0005"),
        wallet_address="walletaddress4tests",
        created_at=datetime.now(UTC).replace(tzinfo=None),
    )


@pytest.fixture
def portfolio_db_model_from_entity(sample_portfolio_entity):
    return PortfolioDBMapper.to_database(sample_portfolio_entity)


@pytest.fixture
def portfolio_entity_from_db_model(sample_portfolio_db_model):
    return PortfolioDBMapper.from_database(sample_portfolio_db_model)


@pytest.fixture
def asset_db_model_from_entity(sample_asset_entity):
    return AssetDBMapper.to_database(sample_asset_entity)


@pytest.fixture
def asset_entity_from_db_model(sample_asset_db_model):
    """Fixture providing Asset database model converted to AssetEntity."""
    return AssetDBMapper.from_database(sample_asset_db_model)


@pytest.fixture
def sample_portfolio_db_mapper():
    """Fixture providing PortfolioDBMapper class for testing."""
    return PortfolioDBMapper


@pytest.fixture
def sample_asset_db_mapper():
    """Fixture providing AssetDBMapper class for testing."""
    return AssetDBMapper


@pytest_asyncio.fixture
async def full_mocked_cached_repository(
    mock_redis_client,
) -> CachedPortfolioRepository:
    """Cached Repository with mocked repository"""
    return CachedPortfolioRepository(
        _redis_client=RedisCache(client=mock_redis_client),
        _mapper=PortfolioDBMapper(),
        _original=AsyncMock(spec=SQLAlchemyPortfolioRepository),
    )
