import pytest

from domain.entities.notification import NotificationEntity
from domain.enums.channel import ChannelEnum
from domain.value_objects.message import MessageValueObject
from domain.value_objects.idempotency_key import IdempotencyKeyVO

from infrastructures.database.mappers import NotificationDBMapper


@pytest.fixture
def sample_notification_entity(
        sample_message_value_object,
        sample_email_channel,
        sample_idempotency_key
) -> NotificationEntity:
    """Базовая фикстура для создания NotificationEntity."""
    return NotificationEntity.create(
        channel=sample_email_channel,
        message=sample_message_value_object,
        recipient="test-recipient@cryptoalrt.io",
        idempotency_key=sample_idempotency_key,
    )

@pytest.fixture
def sample_notification_db_model(sample_notification_entity):
    return NotificationDBMapper.to_database_model(sample_notification_entity)

@pytest.fixture
def sample_notification_to_dict(sample_notification_entity):
    return NotificationDBMapper.to_dict(sample_notification_entity)

@pytest.fixture
def sample_notification_entity_with_params(sample_event_id):
    """Фабрика для создания NotificationEntity с кастомными параметрами."""
    def _create(
            channel: ChannelEnum = ChannelEnum.EMAIL,
            msg_text: str = "Text message is already here! Please, change me :)",
            recipient: str = "cryptodmitrii@cryptoalertov.com",
    ):
        return NotificationEntity.create(
            channel=channel,
            message=MessageValueObject(text=msg_text),
            recipient=recipient,
            idempotency_key=IdempotencyKeyVO.build(
                event_id=sample_event_id,
                channel=channel,
            ),
        )
    return _create


@pytest.fixture
def sample_notification_entity_marked_as_failed(sample_notification_entity):
    """Фикстура для NotificationEntity со статусом FAILED."""
    return sample_notification_entity.mark_failed()


@pytest.fixture
def sample_notification_entity_marked_as_sent(sample_notification_entity):
    """Фикстура для NotificationEntity со статусом SENT."""
    return sample_notification_entity.make_sent()


@pytest.fixture
def sample_idempotency_key(sample_event_id, sample_email_channel):
    """Фикстура для создания IdempotencyKeyVO."""
    return IdempotencyKeyVO.build(
        event_id=sample_event_id,
        channel=sample_email_channel
    )
