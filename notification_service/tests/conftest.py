from datetime import datetime, UTC
from uuid import uuid4

import pytest

from domain.entities.notification import NotificationEntity
from domain.enums.channel import ChannelEnum
from domain.value_objects.message import MessageValueObject
from domain.value_objects.idempotency_key import IdempotencyKeyVO

from domain.enums.status import StatusEnum

from domain.entities.user_preference import UserPreferenceEntity


@pytest.fixture
def sample_notification_entity(
        sample_message_value_object,
        sample_email_channel,
        sample_idempotency_key
) -> NotificationEntity:
    return NotificationEntity.create(
        channel=sample_email_channel,
        message=sample_message_value_object,
        recipient="test-recipient@cryptoalrt.io",
        idempotency_key=sample_idempotency_key,
    )

@pytest.fixture
def sample_notification_entity_with_params(sample_event_id):
    def _create(
            channel: ChannelEnum = ChannelEnum.EMAIL,
            msg_text: str = "Text message already here! Please, change me :)",
            recipient: str = "cryptodmitrii@cryptoalertov.com",
            sent_at: datetime | None = None,
            created_at: datetime | None = datetime.now(UTC),
    ):
        return NotificationEntity.create(
            channel=channel,
            message=MessageValueObject(text=msg_text),
            recipient=recipient,
            sent_at=sent_at,
            created_at=created_at,
            idempotency_key=IdempotencyKeyVO.build(
                event_id=sample_event_id,
                channel=channel,
            ),
        )
    return _create

@pytest.fixture
def sample_user_preference_entity() -> UserPreferenceEntity:
    return UserPreferenceEntity.create(
        email="test@mail.com",
        email_enabled=True,
        telegram_id=None,
        telegram_enabled=False,
    )

@pytest.fixture
def sample_idempotency_key(sample_event_id, sample_email_channel):
    return IdempotencyKeyVO.build(
        event_id=sample_event_id,
        channel=sample_email_channel
    )

@pytest.fixture
def sample_notification_entity_marked_as_failed(sample_notification_entity):
    return sample_notification_entity.mark_failed()

@pytest.fixture
def sample_notification_entity_marked_as_sent(sample_notification_entity):
    return sample_notification_entity.make_sent()

@pytest.fixture
def sample_event_id():
    return uuid4()

@pytest.fixture
def sample_email_channel():
    return ChannelEnum.EMAIL

@pytest.fixture
def sample_notification_id():
    return uuid4()

@pytest.fixture
def sample_message_value_object():
    return MessageValueObject(
        text="Test MessageValueObject for tests :)"
    )


