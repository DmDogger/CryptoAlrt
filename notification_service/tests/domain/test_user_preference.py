import dataclasses
from uuid import uuid4

import pytest

from domain.entities.user_preference import UserPreferenceEntity
from domain.exceptions import DomainValidationError


class TestUserPreference:
    """Tests for UserPreferenceEntity domain entity."""

    def test_create_valid_user_preference_entity(self, sample_user_preference_entity):
        """Test creating a valid UserPreferenceEntity with all required fields."""
        assert sample_user_preference_entity.email == "mail@enabled.cryptoalrt.io"
        assert sample_user_preference_entity.id is not None
        assert sample_user_preference_entity.email_enabled is True
        assert sample_user_preference_entity.telegram_enabled is False
        assert sample_user_preference_entity.telegram_id is None

    def test_user_preference_email_disabled(
        self, sample_user_preference_entity_with_disabled_email
    ):
        """Test that set_email_disable() method creates new entity with email_enabled set to False."""
        assert sample_user_preference_entity_with_disabled_email.email_enabled == False

    def test_user_preference_telegram_enabled(
        self,
        sample_user_preference_entity_with_enabled_telegram,
    ):
        """Test that set_telegram_enabled() method creates new entity with telegram_enabled set to True."""
        assert sample_user_preference_entity_with_enabled_telegram.telegram_enabled == True

    def test_user_preference_is_immutable(
        self,
        sample_user_preference_entity,
    ):
        """Test that UserPreferenceEntity is immutable (frozen dataclass) and raises FrozenInstanceError on modification."""
        with pytest.raises(dataclasses.FrozenInstanceError):
            sample_user_preference_entity.email = "frozenclassov@immutabelskiy.com"

    @pytest.mark.parametrize(
        "invalid_email_value",
        [
            "",
            "big_string" * 100,
        ],
    )
    def test_invalid_email_length(self, invalid_email_value, sample_user_preference_entity):
        """Test that creating UserPreferenceEntity with email length outside 5-100 characters raises DomainValidationError."""
        with pytest.raises(DomainValidationError):
            UserPreferenceEntity(
                id=uuid4(),
                email=invalid_email_value,
                email_enabled=True,
                telegram_id=None,
                telegram_enabled=False,
            )
