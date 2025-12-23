import pytest

from domain.entities.user_preference import UserPreferenceEntity


@pytest.fixture
def sample_user_preference_entity():
    return UserPreferenceEntity.create(
        email="mail@enabled.cryptoalrt.io",
        email_enabled=True,
        telegram_id=None,
        telegram_enabled=False,
    )

@pytest.fixture
def sample_user_preference_entity_with_disabled_email():
    return UserPreferenceEntity.create(
        email="mail@disabled.cryptoalrt.io",
        email_enabled=False,
        telegram_id=None,
        telegram_enabled=False,
    )


@pytest.fixture
def sample_user_preference_entity_with_enabled_telegram():
    return UserPreferenceEntity.create(
        email="telegram@enabled.cryptoalrt.io",
        email_enabled=True,
        telegram_id=None,
        telegram_enabled=True,
    )

