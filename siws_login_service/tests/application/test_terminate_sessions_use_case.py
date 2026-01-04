import pytest


class TestTerminateSessionsUC:
    @pytest.mark.asyncio
    async def test_sessions_terminates_correctly(
        self,
        sample_wallet_session_vo,
        sample_wallet_entity,
        fake_wallet_repository,
        mock_terminate_sessions_uc
    ):


        wallet_address = sample_wallet_entity.wallet_address.value
        await fake_wallet_repository.create_wallet(sample_wallet_entity)
        await fake_wallet_repository.save_session(sample_wallet_session_vo)

        res = await mock_terminate_sessions_uc.execute(wallet_address=wallet_address)

        assert isinstance(res, list)
        assert len(res) == 1