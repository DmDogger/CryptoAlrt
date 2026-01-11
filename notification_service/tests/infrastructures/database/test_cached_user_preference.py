import pytest

from domain.entities.user_preference import UserPreferenceEntity


class TestCachedUserPreferenceRepository:
    @pytest.mark.asyncio
    async def test_get_by_id_from_cache(
        self,
        mock_fake_preference_repository: "FakeUserPreferenceRepository",
        sample_user_preference_entity: UserPreferenceEntity,
        mock_redis_client: "RedisClient",
        mock_cached_repository: "CachedUserPreferenceRepository",
    ):

        await mock_fake_preference_repository.save(sample_user_preference_entity)
        await mock_cached_repository.get_by_id(sample_user_preference_entity.id) # first call: data not cached yet
        cached = await mock_cached_repository.get_by_id(sample_user_preference_entity.id) # second call: data must be cached

        assert cached is not None
        assert isinstance(cached, UserPreferenceEntity)
        assert cached.email_enabled is True
        assert cached.telegram_enabled is False
        assert cached.telegram_id is None
