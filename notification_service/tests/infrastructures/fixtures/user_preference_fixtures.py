import pytest

from domain.entities.user_preference import UserPreferenceEntity


@pytest.fixture
def sample_user_preference_entity():
    return UserPreferenceEntity.create(
        email="user@preferencov.com",
        email_enabled=True,
        telegram_id=None,
        telegram_enabled=False,
    )

@pytest.fixture
def sample_user_preference_entity_with_disabled_email(
    sample_user_preference_entity
):
    return sample_user_preference_entity.set_email_disable()


@pytest.fixture
def sample_user_preference_entity_with_enabled_telegram(
    sample_user_preference_entity,
):
    return sample_user_preference_entity.set_telegram_enabled()

