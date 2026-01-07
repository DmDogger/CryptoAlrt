import pytest


class TestRevokeSessionUC:
    @pytest.mark.asyncio
    async def test_session_terminates_correct(
        self,
        mock_revoke_session_uc,
        fake_wallet_repository,
        sample_wallet_entity,
        sample_wallet_session_vo,
    ):

        wallet_address = sample_wallet_entity.wallet_address.value
        await fake_wallet_repository.create_wallet(sample_wallet_entity)
        await fake_wallet_repository.save_session(sample_wallet_session_vo)

        terminated = await mock_revoke_session_uc.execute(
            wallet_address=wallet_address,
            device_id=sample_wallet_session_vo.device_id,
        )

        assert terminated.is_revoked is True
        assert terminated.device_id is not None
