from typing import AsyncIterable

import aiosmtplib
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.engine.url import make_url

from config.database import db_settings
from config.smtp import smtp_settings
from application.interfaces.email_client import EmailClientProtocol
from application.interfaces.repositories import (
    NotificationRepositoryProtocol,
    PreferenceRepositoryProtocol,
)
from application.use_cases.check_and_reserve import CheckAndReserveUseCase
from application.use_cases.process_alert_triggered_use_case import ProcessAlertTriggeredUseCase
from application.use_cases.send_email_notification import SendEmailNotificationUseCase
from infrastructures.database.mappers.notification_db_mapper import NotificationDBMapper
from infrastructures.database.mappers.user_preference_db_mapper import UserPreferenceDBMapper
from infrastructures.database.repositories.notification import SQLAlchemyNotificationRepository
from infrastructures.database.repositories.user_preference import SQLAlchemyUserPreferenceRepository
from infrastructures.smtp.send_email import SMTPEmailClient


class InfrastructureProvider(Provider):
    """Провайдер для инфраструктурного слоя."""

    @provide(scope=Scope.APP)
    def get_db_engine(self) -> AsyncEngine:
        # Avoid connecting at import time; engine is lazy.
        return create_async_engine(str(make_url(db_settings.database_url)), echo=False)

    @provide(scope=Scope.APP)
    def get_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def get_db_session(self, sessionmaker: async_sessionmaker[AsyncSession]) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            yield session

    @provide(scope=Scope.APP)
    def get_notification_db_mapper(self) -> NotificationDBMapper:
        return NotificationDBMapper()

    @provide(scope=Scope.APP)
    def get_user_preference_db_mapper(self) -> UserPreferenceDBMapper:
        return UserPreferenceDBMapper()

    @provide(scope=Scope.REQUEST)
    def get_notification_repository(
        self,
        session: AsyncSession,
        mapper: NotificationDBMapper,
    ) -> NotificationRepositoryProtocol:
        return SQLAlchemyNotificationRepository(session=session, mapper=mapper)

    @provide(scope=Scope.REQUEST)
    def get_preference_repository(
        self,
        session: AsyncSession,
        mapper: UserPreferenceDBMapper,
    ) -> PreferenceRepositoryProtocol:
        return SQLAlchemyUserPreferenceRepository(session=session, mapper=mapper)
    
    @provide(scope=Scope.REQUEST)
    async def get_smtp_client(self) -> AsyncIterable[aiosmtplib.SMTP]:
        """SMTP client для каждого запроса с контекстным менеджером."""
        smtp = aiosmtplib.SMTP(
            hostname=smtp_settings.host,
            port=smtp_settings.port,
            use_tls=smtp_settings.use_tls,
        )
        await smtp.connect()
        if smtp_settings.username and smtp_settings.password:
            await smtp.login(smtp_settings.username, smtp_settings.password)
        try:
            yield smtp
        finally:
            await smtp.quit()

    @provide(scope=Scope.REQUEST)
    def get_email_client(self, smtp: aiosmtplib.SMTP) -> EmailClientProtocol:
        return SMTPEmailClient(smtp=smtp)


class UseCaseProvider(Provider):
    """Провайдеры use case'ов (application layer)."""

    @provide(scope=Scope.REQUEST)
    def get_check_and_reserve_uc(
        self,
        notification_repository: NotificationRepositoryProtocol,
        preference_repository: PreferenceRepositoryProtocol,
    ) -> CheckAndReserveUseCase:
        return CheckAndReserveUseCase(
            notification_repository=notification_repository,
            preference_repository=preference_repository,
        )

    @provide(scope=Scope.REQUEST)
    def get_send_email_uc(
        self,
        email_client: EmailClientProtocol,
        notification_repository: NotificationRepositoryProtocol,
    ) -> SendEmailNotificationUseCase:
        return SendEmailNotificationUseCase(
            email_client=email_client,
            repository=notification_repository,
        )

    @provide(scope=Scope.REQUEST)
    def get_process_alert_triggered_uc(
        self,
        check_and_reserve_use_case: CheckAndReserveUseCase,
        send_email_use_case: SendEmailNotificationUseCase,
    ) -> ProcessAlertTriggeredUseCase:
        return ProcessAlertTriggeredUseCase(
            check_and_reserve_use_case=check_and_reserve_use_case,
            send_email_use_case=send_email_use_case,
        )
