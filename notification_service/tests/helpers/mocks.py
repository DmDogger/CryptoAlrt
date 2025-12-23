from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import aiosmtplib
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from application.use_cases.send_email_notification import SendEmailNotificationUseCase
from tests.helpers.fakes import FakeRepository, FakeUserPreferenceRepository
from application.use_cases.check_and_reserve import CheckAndReserveUseCase

from tests.infrastructures.fixtures.notification_fixtures import (
    sample_notification_entity_marked_as_failed,
    sample_notification_entity,
    sample_notification_entity_marked_as_sent
)
from tests.infrastructures.fixtures.user_preference_fixtures import (
    sample_user_preference_entity,
    sample_user_preference_entity_with_disabled_email,
)
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
    """Реальный SQLAlchemyNotificationRepository с мок-сессией для тестов."""
    return SQLAlchemyNotificationRepository(
        session=mock_async_session,
        mapper=mock_notification_mapper,
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
        mapper=mock_notification_mapper,
    )

@pytest.fixture
def mock_smtp() -> AsyncMock:
    """Мок SMTP клиента для тестов email отправки."""
    smtp_mock = AsyncMock(spec=aiosmtplib.SMTP)
    return smtp_mock


@pytest.fixture
def mock_email_client(mock_smtp: AsyncMock) -> SMTPEmailClient:
    """Мок SMTPEmailClient с переопределенным методом send для тестов."""
    email = SMTPEmailClient(smtp=mock_smtp)
    email.send = AsyncMock()
    return email


@pytest.fixture
def mock_send_email_use_case(
    mock_email_client: SMTPEmailClient,
    mock_notification_repository: AsyncMock,
    mock_fake_repository: FakeRepository,
) -> SendEmailNotificationUseCase:
    """Мок SendEmailNotificationUseCase с fake репозиторием для тестов."""
    return SendEmailNotificationUseCase(
        email_client=mock_email_client,
        repository=mock_fake_repository,
    )

@pytest.fixture
def mock_fake_repository(
    sample_notification_entity_marked_as_sent,
    sample_notification_entity,
    sample_notification_entity_marked_as_failed,
) -> FakeRepository:
    """Fake in-memory repository для тестов use cases с предзаполненными данными."""
    return FakeRepository(
        preferences=(
            # sample_notification_entity_marked_as_sent,
            sample_notification_entity,
            # sample_notification_entity_marked_as_failed,
        )
    )

@pytest.fixture
def mock_fake_preference_repository(
    sample_user_preference_entity,
    sample_user_preference_entity_with_disabled_email,
    sample_user_preference_entity_with_enabled_telegram,
) -> FakeUserPreferenceRepository:
    """Fake in-memory preference repository для тестов use cases."""
    return FakeUserPreferenceRepository(
        preferences=(
            sample_user_preference_entity,
            sample_user_preference_entity_with_disabled_email,
            sample_user_preference_entity_with_enabled_telegram,
        )
    )


@pytest.fixture
def mock_preference_repository() -> AsyncMock:
    """Мок PreferenceRepository для тестов use cases."""
    repository = AsyncMock()
    repository.get_by_id = AsyncMock()
    repository.save = AsyncMock()
    repository.get_by_idempotency_key = AsyncMock()
    return repository


@pytest.fixture
def mock_check_and_reserve_use_case(
    mock_fake_repository: FakeRepository,
    mock_fake_preference_repository: FakeUserPreferenceRepository,
) -> CheckAndReserveUseCase:
    """Мок CheckAndReserveUseCase с fake репозиториями для тестов."""
    return CheckAndReserveUseCase(
        notification_repository=mock_fake_repository,
        preference_repository=mock_fake_preference_repository,
    )


