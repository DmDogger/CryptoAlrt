from uuid import uuid4

import pytest

from domain.enums.channel import ChannelEnum
from domain.value_objects.message import MessageValueObject

from domain.enums.status import StatusEnum

pytest_plugins = [
    "tests.infrastructures.fixtures.user_preference_fixtures",
    "tests.infrastructures.fixtures.notification_fixtures",
    "tests.helpers.mocks",
]

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

@pytest.fixture
def sample_pending_status():
    return StatusEnum.PENDING


