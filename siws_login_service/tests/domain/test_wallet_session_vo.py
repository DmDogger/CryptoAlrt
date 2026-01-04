import pytest
from freezegun import freeze_time

from src.domain.exceptions import TokenValidationError


class TestWalletSessionVO:
    @freeze_time("2030-01-01 08:00:00")
    def test_wallet_session_initiates_correctly(self, sample_wallet_session_vo):
        assert sample_wallet_session_vo.wallet_address is not None
        assert sample_wallet_session_vo.wallet_address.value == "5cRypRAdKEUtMCyFdqtEifWER5GMCfVnhZ8EUtcB7Sc3"
        assert sample_wallet_session_vo.is_revoked is False
        assert sample_wallet_session_vo.created_at is not None

    @freeze_time("2030-01-01 08:00:00")
    def test_wallet_revoke_works_correctly(self, sample_wallet_session_vo):
        revoked = sample_wallet_session_vo.revoke()

        assert revoked is not None
        assert revoked.is_revoked is True

    def test_raises_token_validation_error(self, wallet_session_with_custom_fields):
        with pytest.raises(TokenValidationError):
            wallet_session_with_custom_fields(
                wallet_address="5cRypRAdKEUtMCyFdqtEifWER5GMCfVnhZ8EUtcB7Sc3",
                refresh_token_hash="vv",
                device_id=3,
        )


