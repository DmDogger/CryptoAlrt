from dataclasses import replace
from datetime import datetime, UTC, timedelta
from decimal import Decimal
from random import randint
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from src.domain.entities.mp_entity import MPEntity

from domain.entities.asset_entity import AssetEntity
from domain.entities.portfolio_entity import PortfolioEntity
from domain.events.price_updated import PriceUpdatedEvent

from domain.value_objects.analytics_vo import AnalyticsValueObject


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
def sample_custom_portfolio_entity(sample_asset_entity):
    def _create(
        wallet_address: str | None = None,
        assets_counted: int | None = None,
        asset_counted: int | None = None,
        assets_count: int | None = None,
        asset_counts: int | None = None,
        total_value: Decimal | None = None,
        weight: Decimal | None = None,
    ):
        final_assets_counted = assets_counted or asset_counted
        final_assets_count = assets_count or asset_counts

        return PortfolioEntity(
            wallet_address=wallet_address if wallet_address else f"wallet_address{randint(1,200)}",
            assets=[sample_asset_entity] * (final_assets_counted or 1),
            total_value=total_value if total_value else Decimal("100"),
            weight=weight if weight else Decimal("100"),
            portfolio_total=Decimal("2000.00"),
            assets_count=final_assets_count if final_assets_count else 1,
            updated_at=datetime.now(UTC) - timedelta(days=2),
        )

    return _create


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


@pytest.fixture
def sample_analytics_vo():
    return AnalyticsValueObject.create(
        ticker="BTC",
    )


@pytest.fixture
def row_obj():
    row = MagicMock()
    row.ticker = "BTC"
    row.position_value = Decimal("1")
    row.allocation = Decimal("10")
    row.port_change = Decimal("1.0")
    row.amount = Decimal("22")
    row.current_price = Decimal("50000")
    return row
