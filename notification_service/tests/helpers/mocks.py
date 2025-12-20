from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructures.database.mappers import NotificationDBMapper
from infrastructures.database.repositories import SQLAlchemyNotificationRepository


@pytest.fixture
def mock_async_session():
    """Мок AsyncSession для тестов репозиториев."""
    session = AsyncMock(spec=AsyncSession)
    session.scalars = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.get = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    return session

@pytest.fixture
def repository(
        mock_async_session,
        mock_notification_mapper,
):
    return SQLAlchemyNotificationRepository(
        session=mock_async_session,
        mapper=mock_notification_mapper
    )


@pytest.fixture
def mock_notification_mapper():
    """Мок NotificationDBMapper для тестов репозиториев."""
    mapper = MagicMock(spec=NotificationDBMapper)
    mapper.to_database_model = MagicMock()
    mapper.from_database_model = MagicMock()
    return mapper



@pytest.fixture
def notification_repository(mock_async_session, mock_notification_mapper):
    """
    Репозиторий с уже настроенной сессией для тестов get_by_id.
    
    Использует configured_mock_session, которая автоматически
    возвращает mock_scalars_result при вызове scalars().
    """
    return SQLAlchemyNotificationRepository(
        session=mock_async_session,
        mapper=mock_notification_mapper
    )