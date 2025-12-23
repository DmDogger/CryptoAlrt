from unittest.mock import AsyncMock, MagicMock

import pytest

from application.use_cases.send_email_notification import SendEmailNotificationUseCase
from domain.entities.notification import NotificationEntity
from domain.enums.status import StatusEnum

from tests.helpers.fakes import FakeRepository

from application.interfaces import EmailClientProtocol
from domain.exceptions import EmailSendingError
from infrastructures.database.repositories import SQLAlchemyNotificationRepository
from infrastructures.smtp.send_email import SMTPEmailClient


class TestSendEmailUseCase:

    @pytest.mark.parametrize(
        "notification_to_be_multiplied",
        [1, 2, 3, 4, 5]
    )
    @pytest.mark.asyncio
    async def test_correct_sending_email_use_case(
            self,
            mock_email_client: AsyncMock,
            mock_send_email_use_case: SendEmailNotificationUseCase,
            sample_notification_entity: NotificationEntity,
            mock_fake_repository: FakeRepository,
            notification_to_be_multiplied: int,
    ) -> None:
        """Test that execute successfully sends email and updates notification status to SENT."""
        #arrange
        notification_id = sample_notification_entity.id
        notifications = [sample_notification_entity] * notification_to_be_multiplied

        #act
        await mock_send_email_use_case.execute(notifications)
        updated = await mock_fake_repository.get_by_id(notification_id)

        #assert
        mock_email_client.send.assert_called()
        assert updated.id is not None
        assert updated.status == StatusEnum.SENT

    @pytest.mark.asyncio
    async def test_send_email_with_empty_list(
            self,
            mock_send_email_use_case: SendEmailNotificationUseCase,
            mock_fake_repository: FakeRepository,
            mock_email_client: EmailClientProtocol,
            sample_notification_entity: NotificationEntity,
    ) -> None:
        """Test that execute returns early without processing when notifications list is empty."""
        #arrange
        notifications = []

        #act
        await mock_send_email_use_case.execute(notifications)

        #assert
        mock_email_client.send.assert_not_called()

    @pytest.mark.parametrize(
        "exception_",
        [
            EmailSendingError,
            Exception
        ]
    )
    @pytest.mark.asyncio
    async def test_send_email_with_exceptions(
            self,
        mock_send_email_use_case: SendEmailNotificationUseCase,
        sample_notification_entity: NotificationEntity,
        mock_email_client: SMTPEmailClient,
            exception_: type[Exception] | type[EmailSendingError],
            mock_fake_repository: FakeRepository,
    ) -> None:
        """Test that execute handles exceptions during email sending and updates notification status to FAILED."""
        #arrange
        notifications = [sample_notification_entity]
        mock_email_client.send.side_effect = exception_
        notification_id = sample_notification_entity.id

        #act
        await mock_send_email_use_case.execute(notifications)
        failed = await mock_fake_repository.get_by_id(notification_id)

        #assert
        assert failed is not None
        assert failed.status == StatusEnum.FAILED







