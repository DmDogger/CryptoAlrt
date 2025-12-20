from datetime import datetime, UTC, timedelta
from uuid import uuid4

import pytest
from domain.enums.channel import ChannelEnum

from domain.enums.status import StatusEnum

from domain.entities.notification import NotificationEntity
from domain.exceptions import DomainValidationError


class TestNotificationEntity:
    def test_create_valid_notification_entity(
            self,
            sample_notification_entity
    ):
        """ Test creating a valid notification"""
        assert sample_notification_entity.recipient == "test-recipient@cryptoalrt.io"
        assert sample_notification_entity.message.text == "Test MessageValueObject for tests :)"
        assert sample_notification_entity.channel == ChannelEnum.EMAIL
        assert sample_notification_entity.status == StatusEnum.PENDING
        assert sample_notification_entity.sent_at is None

    def test_notification_entity_mark_as_sent(
            self,
            sample_notification_entity_marked_as_sent
    ):
        assert sample_notification_entity_marked_as_sent.sent_at is not None
        assert sample_notification_entity_marked_as_sent.status == StatusEnum.SENT

    def test_notification_entity_mark_as_failed(
            self,
            sample_notification_entity_marked_as_failed,
    ):
        assert sample_notification_entity_marked_as_failed.status == StatusEnum.FAILED

    def test_notification_entity_with_empty_message(
            self,
            sample_notification_entity_with_params
    ):
        with pytest.raises(DomainValidationError):
            sample_notification_entity_with_params(msg_text="")

    @pytest.mark.parametrize("invalid_channel",
                             [
                                None,
                                True,
                                "This string is not Enum",
                                1000,
                                -15,
                                StatusEnum
                              ]
                             )
    def test_notification_entity_channel_not_enum(
            self,
            sample_idempotency_key,
            sample_message_value_object,
            invalid_channel,
            sample_notification_entity_with_params
    ):
        with pytest.raises(DomainValidationError):
            NotificationEntity(
                id=uuid4(),
                message=sample_message_value_object,
                recipient="validov@recipientski.com",
                idempotency_key=sample_idempotency_key,
                channel=invalid_channel,
                status=StatusEnum.PENDING,
                sent_at=None,
                created_at=datetime.now(UTC),
            )

    def test_incorrect_datetime(
            self,
            sample_notification_entity_with_params,
            sample_message_value_object,
            sample_idempotency_key,
    ):
        date_in_past = datetime.now(UTC) - timedelta(days=5)

        with pytest.raises(DomainValidationError):
            NotificationEntity(
                id=uuid4(),
                message=sample_message_value_object,
                recipient="validov@recipientski.com",
                idempotency_key=sample_idempotency_key,
                channel=ChannelEnum.EMAIL,
                status=StatusEnum.PENDING,
                sent_at=date_in_past,
                created_at=datetime.now(UTC),
            )





