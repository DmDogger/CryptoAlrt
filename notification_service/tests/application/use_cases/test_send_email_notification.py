from unittest.mock import AsyncMock, MagicMock

import pytest

from application.use_cases.send_email_notification import SendEmailNotificationUseCase
from domain.entities.notification import NotificationEntity
from domain.enums.status import StatusEnum
from domain.exceptions import EmailSendingError
from infrastructures.database.repositories import SQLAlchemyNotificationRepository
from infrastructures.smtp.send_email import SMTPEmailClient


class TestSendEmailUseCase:
    @pytest.mark.asyncio
    async def test_correct_sending_email_use_case(
            self,
            mock_email_client: AsyncMock,
            mock_send_email_use_case: SendEmailNotificationUseCase,
            sample_notification_entity_marked_as_sent: NotificationEntity,
            sample_notification_entity: NotificationEntity,
            repository: "SQLAlchemyNotificationRepository",
    ) -> None:
        """Test that execute successfully sends email and updates notification status to SENT."""
        #arrange
        notifications = [sample_notification_entity]
        updated_notification = sample_notification_entity_marked_as_sent

        #act
        await mock_send_email_use_case.execute(notifications)

        #assert
        mock_email_client.send.assert_called_once()
        assert updated_notification.status == StatusEnum.SENT

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
            sample_notification_entity_marked_as_failed: NotificationEntity,
            mock_email_client: SMTPEmailClient,
            exception_: type[Exception] | type[EmailSendingError],
            mock_notification_repository: AsyncMock,
    ) -> None:
        """Test that execute handles exceptions during email sending and updates notification status to FAILED."""
        notifications = [sample_notification_entity]
        failed_notification = sample_notification_entity_marked_as_failed

        mock_email_client.send.side_effect = exception_
        await mock_send_email_use_case.execute(notifications)


        assert failed_notification.status == StatusEnum.FAILED
        mock_notification_repository.update.assert_called_once()







