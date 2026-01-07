import pytest

from domain.events.alert_triggered import AlertTriggeredEvent
from application.use_cases.check_and_reserve import CheckAndReserveUseCase
from tests.helpers.fakes import FakeUserPreferenceRepository, FakeRepository
from domain.entities.user_preference import UserPreferenceEntity
from domain.value_objects.idempotency_key import IdempotencyKeyVO
from domain.enums.channel import ChannelEnum


class TestCheckAndReserveUseCase:
    @pytest.mark.asyncio
    async def test_email_enabled_case(
        self,
        sample_user_preference_entity: UserPreferenceEntity,
        mock_check_and_reserve_use_case: CheckAndReserveUseCase,
        mock_fake_preference_repository: FakeUserPreferenceRepository,
        mock_fake_repository: FakeRepository,
        sample_alert_triggered_event: AlertTriggeredEvent,
    ) -> None:
        """Test that execute creates email notification when email channel is enabled.

        Verifies that:
        - Use case returns list with one notification
        - User preference is found and has correct email settings
        - Notification is created and can be found by idempotency_key
        - Notification has correct channel and recipient
        """
        use_case_result = await mock_check_and_reserve_use_case.execute(
            sample_alert_triggered_event
        )
        result_from_preference = await mock_fake_preference_repository.get_by_email(
            sample_user_preference_entity.email
        )

        idempotency_key_for_email = IdempotencyKeyVO.build(
            event_id=sample_alert_triggered_event.id,
            channel=ChannelEnum.EMAIL,
        )
        result_from_notification = await mock_fake_repository.get_by_idempotency_key(
            idempotency_key_for_email.key
        )

        assert len(use_case_result) == 1
        assert result_from_preference is not None
        assert result_from_preference.email_enabled is True
        assert result_from_preference.email == "mail@enabled.cryptoalrt.io"

        assert result_from_preference.telegram_enabled is False
        assert result_from_notification is not None
        assert result_from_notification.channel == ChannelEnum.EMAIL
        assert result_from_notification.recipient == sample_user_preference_entity.email
