from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock
import pytest
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from domain.entities.notification import NotificationEntity
from domain.enums.status import StatusEnum
from domain.exceptions import RepositoryError
from domain.value_objects.idempotency_key import IdempotencyKeyVO
from ..fixtures.notification_fixtures import (
    sample_notification_entity,
    sample_idempotency_key,
)
from ...helpers.mocks import mock_async_session, repository

if TYPE_CHECKING:
    from infrastructures.database.models.notification import Notification
    from infrastructures.database.repositories import SQLAlchemyNotificationRepository


class TestSQLAlchemyNotificationRepository:
    @pytest.mark.asyncio
    async def test_get_by_id_not_none(
        self,
        repository: "SQLAlchemyNotificationRepository",
        mock_async_session: AsyncMock,
        sample_notification_db_model: "Notification",
        sample_notification_entity: NotificationEntity,
        mock_notification_mapper: MagicMock,
    ) -> None:
        """Test that get_by_id returns NotificationEntity when notification is found."""
        # arrange
        notification_id = sample_notification_entity.id
        mock_res = MagicMock()
        mock_res.first.return_value = sample_notification_db_model
        mock_async_session.scalars.return_value = mock_res
        mock_notification_mapper.from_database_model.return_value = (
            sample_notification_entity
        )

        # act
        result = await repository.get_by_id(notification_id)

        # assert
        assert result == sample_notification_entity
        mock_async_session.scalars.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_is_none(
        self,
        repository: "SQLAlchemyNotificationRepository",
        sample_notification_entity: NotificationEntity,
        mock_async_session: AsyncMock,
    ) -> None:
        """Test that get_by_id returns None when notification is not found."""
        # arrange
        notification_id = sample_notification_entity.id
        mock_res = MagicMock()
        mock_res.first.return_value = None

        mock_async_session.scalars.return_value = mock_res

        # act
        result = await repository.get_by_id(notification_id)

        # assert
        assert result is None
        mock_async_session.scalars.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_status(
        self,
        sample_notification_db_model: "Notification",
        mock_notification_mapper: MagicMock,
        mock_async_session: AsyncMock,
        sample_notification_entity: NotificationEntity,
        sample_pending_status: StatusEnum,
        repository: "SQLAlchemyNotificationRepository",
    ) -> None:
        """Test that get_by_status returns list of NotificationEntity when notifications are found."""
        # arrange
        mock_res = MagicMock()
        mock_res.all.return_value = [sample_notification_db_model]

        mock_async_session.scalars.return_value = mock_res
        mock_notification_mapper.from_database_model.return_value = (
            sample_notification_entity
        )

        expected_result = [sample_notification_entity]

        # act

        result = await repository.get_by_status(sample_pending_status)

        # assert

        assert result == expected_result
        mock_async_session.scalars.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_status_empty_list(
        self,
        sample_pending_status: StatusEnum,
        mock_async_session: AsyncMock,
        repository: "SQLAlchemyNotificationRepository",
    ) -> None:
        """Test that get_by_status returns empty list when no notifications are found."""
        # arrange
        mock_res = MagicMock()
        mock_res.all.return_value = []

        mock_async_session.scalars.return_value = mock_res

        expected_entities = []

        # act
        result = await repository.get_by_status(sample_pending_status)

        # assert
        assert result == expected_entities
        mock_async_session.scalars.assert_called_once()

    @pytest.mark.asyncio
    async def test_correct_saved_entity(
        self,
        sample_notification_db_model: "Notification",
        sample_notification_entity: NotificationEntity,
        notification_repository: "SQLAlchemyNotificationRepository",
        mock_notification_mapper: MagicMock,
        mock_async_session: AsyncMock,
        repository: "SQLAlchemyNotificationRepository",
    ) -> None:
        """Test that save successfully saves notification entity and returns saved entity."""
        # arrange
        mock_notification_mapper.to_database_model.return_value = (
            sample_notification_db_model
        )
        mock_notification_mapper.from_database_model.return_value = (
            sample_notification_entity
        )

        res_obj = MagicMock()
        res_obj.get.return_value = sample_notification_db_model

        mock_async_session.get.return_value = res_obj.get.return_value

        # act
        result = await repository.save(sample_notification_entity)

        # assert
        assert result.id is not None
        assert result == sample_notification_entity
        mock_async_session.get.assert_called_once()
        mock_async_session.add.assert_called_once()
        mock_async_session.commit.assert_called_once()
        mock_notification_mapper.to_database_model.assert_called_with(
            sample_notification_entity
        )
        mock_notification_mapper.from_database_model.assert_called_with(
            sample_notification_db_model
        )

    @pytest.mark.asyncio
    async def test_correct_updated_entity(
        self,
        repository: "SQLAlchemyNotificationRepository",
        mock_async_session: AsyncMock,
        mock_notification_mapper: MagicMock,
        sample_notification_db_model: "Notification",
        sample_notification_entity: NotificationEntity,
        sample_notification_to_dict: dict,
    ) -> None:
        """Test that update successfully updates notification entity and returns updated entity."""
        # arrange
        result_obj = MagicMock()
        result_obj.scalar_one.return_value = sample_notification_db_model

        mock_notification_mapper.to_dict.return_value = sample_notification_to_dict
        mock_notification_mapper.from_database_model.return_value = (
            sample_notification_entity
        )

        mock_async_session.execute.return_value = result_obj

        # act
        result = await repository.update(sample_notification_entity)

        # assert
        assert result == sample_notification_entity
        mock_async_session.execute.assert_called_once()
        mock_notification_mapper.to_dict.assert_called_with(sample_notification_entity)
        mock_notification_mapper.from_database_model.assert_called_with(
            sample_notification_db_model
        )

    @pytest.mark.asyncio
    async def test_get_by_idempotency_key(
        self,
        sample_idempotency_key: IdempotencyKeyVO,
        repository: "SQLAlchemyNotificationRepository",
        sample_notification_entity: NotificationEntity,
        mock_async_session: AsyncMock,
        sample_notification_db_model: "Notification",
        mock_notification_mapper: MagicMock,
    ) -> None:
        """Test that get_by_idempotency_key returns NotificationEntity when notification is found."""
        # arrange
        result_obj = MagicMock()
        result_obj.first.return_value = sample_notification_db_model

        mock_async_session.scalars.return_value = result_obj
        mock_notification_mapper.from_database_model.return_value = (
            sample_notification_entity
        )

        # act

        result = await repository.get_by_idempotency_key(sample_idempotency_key)

        assert result.id is not None
        mock_async_session.scalars.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_none_by_idempotency_key(
        self,
        mock_async_session: AsyncMock,
        sample_idempotency_key: IdempotencyKeyVO,
        repository: "SQLAlchemyNotificationRepository",
    ) -> None:
        """Test that get_by_idempotency_key returns None when notification is not found."""
        # arrange
        res_obj = MagicMock()
        res_obj.first.return_value = None

        mock_async_session.scalars.return_value = res_obj

        # act

        result = await repository.get_by_idempotency_key(sample_idempotency_key)

        # assert
        assert result is None
        mock_async_session.scalars.assert_called_once()

    @pytest.mark.parametrize(
        "exception_",
        [
            IntegrityError(params=None, statement="", orig=None),
            SQLAlchemyError,
            Exception,
            RepositoryError,
        ],
    )
    @pytest.mark.asyncio
    async def test_incorrect_updated_with_errors(
        self,
        sample_notification_entity: NotificationEntity,
        mock_async_session: AsyncMock,
        repository: "SQLAlchemyNotificationRepository",
        mock_notification_mapper: MagicMock,
        exception_,
    ):

        mock_async_session.execute.side_effect = exception_

        with pytest.raises(RepositoryError):
            await repository.update(sample_notification_entity)

        mock_async_session.rollback.assert_called_once()
        mock_async_session.commit.assert_not_called()
        mock_notification_mapper.to_dict.assert_called_with(sample_notification_entity)
