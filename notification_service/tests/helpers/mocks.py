from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import aiosmtplib
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from application.use_cases.send_email_notification import SendEmailNotificationUseCase

from tests.helpers.fakes import FakeRepository
from infrastructures.database.mappers import NotificationDBMapper
from infrastructures.database.repositories import SQLAlchemyNotificationRepository
from infrastructures.smtp.send_email import SMTPEmailClient

if TYPE_CHECKING:
    pass

@pytest.fixture
def mock_async_session() -> AsyncMock:
    """Мок AsyncSession для тестов репозиториев."""
    session = AsyncMock(spec=AsyncSession)
    session.scalars = AsyncMock()
    session.scalar_one = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.get = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    return session

@pytest.fixture
def repository(
        mock_async_session: AsyncMock,
        mock_notification_mapper: MagicMock,
) -> SQLAlchemyNotificationRepository:
    return SQLAlchemyNotificationRepository(
        session=mock_async_session,
        mapper=mock_notification_mapper
    )

@pytest.fixture
def mock_notification_repository() -> AsyncMock:
    """Мок NotificationRepository для тестов use cases."""
    repository = AsyncMock(spec=SQLAlchemyNotificationRepository)
    repository.update = AsyncMock()
    return repository


@pytest.fixture
def mock_notification_mapper() -> MagicMock:
    """Мок NotificationDBMapper для тестов репозиториев."""
    mapper = MagicMock(spec=NotificationDBMapper)
    mapper.to_database_model = MagicMock()
    mapper.from_database_model = MagicMock()
    return mapper



@pytest.fixture
def notification_repository(
        mock_async_session: AsyncMock,
        mock_notification_mapper: MagicMock,
) -> SQLAlchemyNotificationRepository:
    """
    Репозиторий с уже настроенной сессией для тестов get_by_id.

    Использует configured_mock_session, которая автоматически
    возвращает mock_scalars_result при вызове scalars().
    """
    return SQLAlchemyNotificationRepository(
        session=mock_async_session,
        mapper=mock_notification_mapper
    )

@pytest.fixture
def mock_smtp():
    smtp_mock = AsyncMock(spec=aiosmtplib.SMTP)
    return smtp_mock

@pytest.fixture
def mock_email_client(mock_smtp):
    email = SMTPEmailClient(smtp=mock_smtp)
    email.send = AsyncMock()
    return email

@pytest.fixture
def mock_send_email_use_case(
        mock_email_client,
        mock_notification_repository,
        mock_fake_repository,
):
    return SendEmailNotificationUseCase(
        email_client=mock_email_client,
        repository=mock_fake_repository,
    )

@pytest.fixture
def mock_fake_repository() -> FakeRepository:
    """Fake in-memory repository for use case tests."""
    return FakeRepository(preferences=())


