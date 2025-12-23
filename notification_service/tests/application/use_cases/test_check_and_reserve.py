import pytest

from domain.events.alert_triggered import AlertTriggeredEvent
from application.use_cases.check_and_reserve import CheckAndReserveUseCase


class TestCheckAndReserveUseCase:
    @pytest.mark.asyncio
    async def test_correct_way(
            self,
            mock_check_and_reserve_use_case: CheckAndReserveUseCase,
            sample_alert_triggered_event: AlertTriggeredEvent,

    ):
        await mock_check_and_reserve_use_case.execute(sample_alert_triggered_event)





