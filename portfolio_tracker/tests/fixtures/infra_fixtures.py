"""Fixtures for infrastructure layer tests."""

from datetime import datetime, UTC
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import ScalarResult
from unittest.mock import AsyncMock, MagicMock

from infrastructures.database.models.portfolio import Portfolio
from infrastructures.database.models.asset import Asset
from infrastructures.database.models.cryptoprice import CryptoPrice
from infrastructures.database.mappers.portfolio_db_mapper import PortfolioDBMapper
from infrastructures.database.mappers.asset_db_mapper import AssetDBMapper
from infrastructures.database.repositories.portfolio import SQLAlchemyPortfolioRepository


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
