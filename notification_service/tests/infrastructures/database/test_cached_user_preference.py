import pytest

from domain.entities.user_preference import UserPreferenceEntity


class TestCachedUserPreferenceRepository:
    @pytest.mark.asyncio
    async def test_get_by_id_from_cache(
        self,
        mock_fake_preference_repository: "FakeUserPreferenceRepository",
        sample_user_preference_entity: UserPreferenceEntity,
        mock_cached_repository: "CachedUserPreferenceRepository",
    ):

        await mock_fake_preference_repository.save(sample_user_preference_entity)
        res = await mock_cached_repository.get_by_id(sample_user_preference_entity.id)

        assert isinstance(res, UserPreferenceEntity)
        assert res.email_enabled is True
        assert res.telegram_enabled is False
        assert res.telegram_id is None
