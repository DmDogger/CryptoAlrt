from typing import Generator, AsyncGenerator, Any
from unittest.mock import AsyncMock, MagicMock

import aiosmtplib
import pytest
import pytest_asyncio
from dishka import make_async_container, AsyncContainer
from dishka.integrations.faststream import setup_dishka as setup_dishka_faststream
from faststream import app
from faststream.kafka import TestKafkaBroker, KafkaBroker
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from testcontainers.redis import RedisContainer, AsyncRedisContainer

from application.use_cases.send_email_notification import SendEmailNotificationUseCase
from tests.helpers.fakes import FakeRepository, FakeUserPreferenceRepository
from application.use_cases.check_and_reserve import CheckAndReserveUseCase

from tests.infrastructures.fixtures.notification_fixtures import (
    sample_notification_entity_marked_as_failed,
    sample_notification_entity,
    sample_notification_entity_marked_as_sent,
)
from tests.infrastructures.fixtures.user_preference_fixtures import (
    sample_user_preference_entity,
    sample_user_preference_entity_with_disabled_email,
)

from tests.helpers.providers import MockInfrastructureProvider, MockUseCaseProvider

from config.broker import broker_settings
from infrastructures.cache.redis import RedisCache
from infrastructures.consumer.alert_triggered_consumer import consume_alert_triggered
from infrastructures.database.mappers import NotificationDBMapper, UserPreferenceDBMapper
from infrastructures.database.repositories import SQLAlchemyNotificationRepository
from infrastructures.database.repositories.cached_user_preference import (
    CachedUserPreferencyRepository,
)
from infrastructures.smtp.send_email import SMTPEmailClient


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
    return FakeRepository(preferences=(sample_notification_entity,))


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


@pytest.fixture
def container() -> Generator[AsyncContainer, None, None]:
    """Контейнер Дишка"""
    container = make_async_container(
        MockInfrastructureProvider(),
        MockUseCaseProvider(),
    )
    yield container
    container.close()


@pytest.fixture
def mock_broker(container: "AsyncContainer") -> KafkaBroker:
    """Мок Кафки"""
    broker = KafkaBroker(bootstrap_servers=MagicMock())

    setup_dishka_faststream(container, broker=broker, auto_inject=True)

    broker.subscriber(broker_settings.alert_triggered_topic, title="consume_alert_triggered")(
        consume_alert_triggered
    )
    return broker


@pytest_asyncio.fixture
async def mock_redis_client() -> AsyncGenerator[Any, Any]:
    """RedisClient через TestConatiner"""
    with AsyncRedisContainer() as redis_container:
        redis_client = await redis_container.get_async_client()
        yield redis_client
        await redis_client.aclose()


@pytest_asyncio.fixture
async def mock_cached_repository(
    mock_redis_client, mock_fake_preference_repository
) -> CachedUserPreferencyRepository:
    """Cached Repository with injected fake repository"""
    return CachedUserPreferencyRepository(
        _redis_cache=RedisCache(client=mock_redis_client),
        _mapper=UserPreferenceDBMapper(),
        _original=mock_fake_preference_repository,
    )


@pytest_asyncio.fixture
async def full_mocked_cached_repository(
    mock_redis_client, mock_preference_repository
) -> CachedUserPreferencyRepository:
    """Cached Repository with mocked repository"""
    return CachedUserPreferencyRepository(
        _redis_cache=RedisCache(client=mock_redis_client),
        _mapper=UserPreferenceDBMapper(),
        _original=mock_preference_repository,
    )

