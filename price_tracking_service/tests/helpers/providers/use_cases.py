from unittest.mock import AsyncMock

from dishka import provide, Scope, Provider

from application.use_cases.check_threshold import CheckThresholdUseCase

from application.interfaces.event_publisher import EventPublisherProtocol
from application.interfaces.repositories import AlertRepositoryProtocol


class MockUseCasesProvider(Provider):
    @provide(scope=Scope.APP)
    def mock_check_threshold_uc(self) -> CheckThresholdUseCase:
        return CheckThresholdUseCase(
            alert_repository=AsyncMock(spec=AlertRepositoryProtocol),
            event_publisher=AsyncMock(spec=EventPublisherProtocol),
        )
