from datetime import datetime, UTC
from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.entities.mp_entity import MPEntity

from domain.entities.asset_entity import AssetEntity
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
