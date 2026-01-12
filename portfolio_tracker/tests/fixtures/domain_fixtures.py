from dataclasses import replace
from datetime import datetime, UTC, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.entities.mp_entity import MPEntity

from domain.entities.asset_entity import AssetEntity
from domain.entities.portfolio_entity import PortfolioEntity
from domain.events.price_updated import PriceUpdatedEvent


@pytest.fixture
def sample_uuid():
    return uuid4()


@pytest.fixture
def sample_mp_entity(sample_uuid):
    return MPEntity(
        id=sample_uuid,
        cryptocurrency="BTC",
        name="Bitcoin",
        price=Decimal("90_000"),
        timestamp=datetime.now(UTC),
    )


@pytest.fixture
def sample_price_updated_event(sample_uuid):
    return PriceUpdatedEvent(
        id=sample_uuid,
        cryptocurrency="BTC",
        name="Bitcoin",
        price=Decimal("90_000"),
        timestamp=datetime.now(UTC),
    )


@pytest.fixture
def sample_asset_entity(sample_uuid):
    return AssetEntity.create(
        ticker="BTC",
        amount=Decimal("0.0005"),
        wallet_address="walletaddress4tests",
    )


@pytest.fixture
def sample_portfolio_entity(sample_asset_entity):
    """Fixture providing a sample PortfolioEntity instance."""
    return PortfolioEntity(
        wallet_address="walletaddress4tests",
        assets=[sample_asset_entity],
        total_value=None,
        weight=Decimal("50.00"),
        portfolio_total=Decimal("2000.00"),
        assets_count=1,
        updated_at=datetime.now(UTC) - timedelta(days=2),
    )


@pytest.fixture
def sample_empty_portfolio_entity():
    """Portfolio entity without assets."""
    return PortfolioEntity(
        wallet_address="walletaddress4tests",
        assets=None,
        total_value=None,
        weight=None,
        portfolio_total=None,
        assets_count=0,
        updated_at=datetime.now(UTC) - timedelta(days=2),
    )


@pytest.fixture
def unique_wallet_address():
    """Unique wallet address for integration tests to avoid conflicts."""
    return f"wallet_{uuid4().hex[:8]}"


@pytest.fixture
def integration_portfolio_entity(unique_wallet_address, sample_asset_entity):
    """Portfolio entity with unique wallet address for integration tests."""
    asset_with_unique_wallet = replace(sample_asset_entity, wallet_address=unique_wallet_address)
    return PortfolioEntity(
        wallet_address=unique_wallet_address,
        assets=[asset_with_unique_wallet],
        total_value=None,
        weight=Decimal("50.00"),
        portfolio_total=Decimal("2000.00"),
        assets_count=1,
        updated_at=datetime.now(UTC) - timedelta(days=2),
    )


@pytest.fixture
def integration_empty_portfolio_entity(unique_wallet_address):
    """Empty portfolio entity with unique wallet address for integration tests."""
    return PortfolioEntity(
        wallet_address=unique_wallet_address,
        assets=None,
        total_value=None,
        weight=None,
        portfolio_total=None,
        assets_count=0,
        updated_at=datetime.now(UTC) - timedelta(days=2),
    )
