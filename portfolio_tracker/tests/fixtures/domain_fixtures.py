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
        total_value=Decimal("1000.00"),
        weight=Decimal("50.00"),
        portfolio_total=Decimal("2000.00"),
        updated_at=datetime.now(UTC) - timedelta(days=2),
    )
