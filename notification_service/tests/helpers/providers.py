from unittest.mock import AsyncMock, MagicMock

import aiosmtplib

from dishka import provide, Scope, Provider

from application.interfaces import EmailClientProtocol, NotificationRepositoryProtocol
from application.interfaces.repositories import PreferenceRepositoryProtocol
from application.use_cases.check_and_reserve import CheckAndReserveUseCase
from application.use_cases.process_alert_triggered_use_case import ProcessAlertTriggeredUseCase
from application.use_cases.send_email_notification import SendEmailNotificationUseCase
from infrastructures.providers import InfrastructureProvider, UseCaseProvider
from infrastructures.smtp.send_email import SMTPEmailClient


class MockInfrastructureProvider(InfrastructureProvider):
    @provide(scope=Scope.REQUEST)
    async def get_smtp_client(self) -> AsyncMock:
        smtp = AsyncMock(spec=aiosmtplib.SMTP)
        smtp.connect = AsyncMock()
        return smtp

    @provide(scope=Scope.REQUEST)
    def get_email_client(self, get_mock_smtp_client: AsyncMock) -> EmailClientProtocol:
        return SMTPEmailClient(smtp=get_mock_smtp_client)


class MockUseCaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_check_and_reserve_uc(
        self,
    ) -> CheckAndReserveUseCase:
        return CheckAndReserveUseCase(
            notification_repository=AsyncMock(spec=NotificationRepositoryProtocol),
            preference_repository=AsyncMock(spec=PreferenceRepositoryProtocol),
        )

    @provide(scope=Scope.REQUEST)
    def get_send_email_uc(
        self,
        get_email_client: EmailClientProtocol,
    ) -> SendEmailNotificationUseCase:
        return SendEmailNotificationUseCase(
            email_client=get_email_client,
            repository=AsyncMock(spec=NotificationRepositoryProtocol),
        )

    @provide(scope=Scope.REQUEST)
    def get_process_alert_triggered_uc(
        self,
    ) -> ProcessAlertTriggeredUseCase:
        return ProcessAlertTriggeredUseCase(
            check_and_reserve_use_case=AsyncMock(),
            send_email_use_case=AsyncMock(),
        )
