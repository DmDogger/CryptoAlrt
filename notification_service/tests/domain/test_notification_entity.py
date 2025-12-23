import dataclasses
from datetime import datetime, UTC, timedelta
from uuid import uuid4

import pytest
from domain.enums.channel import ChannelEnum

from domain.enums.status import StatusEnum

from domain.entities.notification import NotificationEntity
from domain.exceptions import DomainValidationError
from domain.value_objects.message import MessageValueObject


class TestNotificationEntity:
    """Tests for NotificationEntity domain entity."""

    def test_create_valid_notification_entity(
            self,
            sample_notification_entity
    ):
        """Test creating a valid notification entity with all required fields."""
        assert sample_notification_entity.recipient == "test-recipient@cryptoalrt.io"
        assert sample_notification_entity.message.text == "Test MessageValueObject for tests :)"
        assert sample_notification_entity.channel == ChannelEnum.EMAIL
        assert sample_notification_entity.status == StatusEnum.PENDING
        assert sample_notification_entity.sent_at is None

    def test_notification_entity_mark_as_sent(
            self,
            sample_notification_entity_marked_as_sent
    ):
        """Test that make_sent() method creates new entity with SENT status and sent_at timestamp."""
        assert sample_notification_entity_marked_as_sent.status == StatusEnum.SENT

    def test_notification_entity_mark_as_failed(
            self,
            sample_notification_entity_marked_as_failed,
    ):
        """Test that mark_failed() method creates new entity with FAILED status."""
        assert sample_notification_entity_marked_as_failed.status == StatusEnum.FAILED

    def test_notification_entity_with_empty_message(
            self,
            sample_notification_entity_with_params
    ):
        """Test that creating notification with empty message raises DomainValidationError."""
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
    ):
        """Test that creating notification with invalid channel (not ChannelEnum) raises DomainValidationError."""
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
            sample_message_value_object,
            sample_idempotency_key,
    ):
        """Test that creating notification with sent_at earlier than created_at raises DomainValidationError."""
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

    @pytest.mark.parametrize(
        "invalid_value",
        [
        "test_big_string" * 105,
        "",
    ]
    )
    def test_invalid_recipient_length(
            self,
            invalid_value,
            sample_idempotency_key,
            sample_message_value_object,
    ):
        """Test that creating notification with recipient length outside 1-100 characters raises DomainValidationError."""
        with pytest.raises(DomainValidationError):
            NotificationEntity(
                    id=uuid4(),
                    message=sample_message_value_object,
                    recipient=invalid_value,
                    idempotency_key=sample_idempotency_key,
                    channel=ChannelEnum.EMAIL,
                    status=StatusEnum.PENDING,
                    sent_at=None,
                    created_at=datetime.now(UTC),
                )

    @pytest.mark.parametrize(
        "invalid_value",
        [
            "",
            "giant_test_string" * 100,
        ]
    )
    def test_invalid_message_length(
            self,
            invalid_value,
            sample_idempotency_key,
            sample_message_value_object,
    ):
        """Test that creating notification with message length outside 1-100 characters raises DomainValidationError."""
        with pytest.raises(DomainValidationError):
            NotificationEntity(
                    id=uuid4(),
                    message=MessageValueObject(text=invalid_value),
                    recipient="validov@dmitrii.io",
                    idempotency_key=sample_idempotency_key,
                    channel=ChannelEnum.EMAIL,
                    status=StatusEnum.PENDING,
                    sent_at=None,
                    created_at=datetime.now(UTC),
                )

    def test_entity_is_immutable(
            self,
            sample_notification_entity
    ):
        """Test that NotificationEntity is immutable (frozen dataclass) and raises FrozenInstanceError on modification."""
        with pytest.raises(dataclasses.FrozenInstanceError):
            sample_notification_entity.recipient = 'immutablov@dataclass.comov'



    @pytest.mark.parametrize(
        "invalid_value",
        [
            "Test_string",
            123,
            -505,
            None,
            True,
         ]
    )
    def test_notification_entity_invalid_idempotency_key(
            self,
            sample_message_value_object,
            invalid_value
    ):
        """Test that creating notification with invalid idempotency_key (not IdempotencyKeyVO instance) raises DomainValidationError."""
        with pytest.raises(DomainValidationError):
            NotificationEntity(
                id=uuid4(),
                message=sample_message_value_object,
                recipient="validov@dmitrii.io",
                idempotency_key=invalid_value,
                channel=ChannelEnum.EMAIL,
                status=StatusEnum.PENDING,
                sent_at=None,
                created_at=datetime.now(UTC),
            )