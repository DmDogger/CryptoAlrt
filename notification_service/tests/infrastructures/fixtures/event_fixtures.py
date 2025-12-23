from datetime import datetime
from uuid import uuid4

import pytest

from domain.events.alert_triggered import AlertTriggeredEvent


@pytest.fixture
def sample_alert_triggered_event() -> AlertTriggeredEvent:
    """Базовая фикстура для создания AlertTriggeredEvent."""
    return AlertTriggeredEvent(
        id=str(uuid4()),
        email="test@cryptoalrt.io",
        alert_id=str(uuid4()),
        cryptocurrency="BTC",
        current_price="50000.50",
        threshold_price="50000.00",
        created_at=datetime.now().isoformat(),
        telegram_id=None,
    )
