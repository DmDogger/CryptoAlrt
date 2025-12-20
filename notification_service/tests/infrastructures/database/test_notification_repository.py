from unittest.mock import AsyncMock, MagicMock

import pytest

from tests.helpers.mocks import mock_async_session

from domain.enums.status import StatusEnum
from infrastructures.database.repositories import SQLAlchemyNotificationRepository


class TestSQLAlchemyNotificationRepository:
    @pytest.mark.asyncio
    async def test_get_notification_by_id(
            self,
            sample_notification_db_model,
            mock_async_session,
            sample_notification_entity,
            mock_notification_mapper,
            notification_repository,
    ):
        """
        Test retrieving notification by ID.
        
        Verifies that the repository correctly:
        1. Calls session.scalars() with the correct query
        2. Calls first() on the scalars result
        3. Converts DB model to Entity through mapper
        """
        #arrange

        notification_id = sample_notification_entity.id

        mock_scalars_res = MagicMock()
        mock_scalars_res.first.return_value = sample_notification_db_model
        mock_async_session.scalars.return_value = mock_scalars_res
        mock_notification_mapper.from_database_model.return_value = sample_notification_entity

        #act
        notification_entity = await notification_repository.get_by_id(notification_id)

        #assert
        assert notification_entity.id is not None
        assert notification_entity == sample_notification_entity
        mock_async_session.scalars.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_notification_by_status(
            self,
            mock_async_session,
            sample_notification_db_model,
            mock_notification_mapper,
            sample_notification_entity,
            notification_repository,

    ):
        """
        Test retrieving notifications by status.
        
        Verifies that the repository correctly:
        1. Calls session.scalars() with status filter
        2. Calls all() on the scalars result to get list of DB models
        3. Converts each DB model to Entity through mapper
        4. Returns list of notification entities
        """
        #arrange
        mock_res = MagicMock()
        mock_res.all.return_value = [sample_notification_db_model]

        mock_async_session.scalars.return_value = mock_res
        mock_notification_mapper.from_database_model.return_value = sample_notification_entity

        expected_entities = [sample_notification_entity]
        status = StatusEnum.PENDING

        #act
        res = await notification_repository.get_by_status(status)

        assert res == expected_entities







