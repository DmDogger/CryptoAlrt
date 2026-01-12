from json import JSONDecodeError

import pytest
from redis import DataError

from domain.entities.user_preference import UserPreferenceEntity


class TestCachedUserPreferenceRepository:
    @pytest.mark.asyncio
    async def test_get_by_id_from_cache(
        self,
        mock_fake_preference_repository: "FakeUserPreferenceRepository",
        sample_user_preference_entity: UserPreferenceEntity,
        mock_cached_repository: "CachedUserPreferenceRepository",
    ):
        """Test that data not found -> saved in cached -> found in cache"""

        await mock_fake_preference_repository.save(sample_user_preference_entity)
        await mock_cached_repository.get_by_id(
            sample_user_preference_entity.id
        )  # first call: data not cached yet
        cached = await mock_cached_repository.get_by_id(
            sample_user_preference_entity.id
        )  # second call: data must be cached

        assert cached is not None
        assert isinstance(cached, UserPreferenceEntity)
        assert cached.email_enabled is True
        assert cached.telegram_enabled is False
        assert cached.telegram_id is None

    @pytest.mark.asyncio
    async def test_save_entity_to_cache(
        self, sample_user_preference_entity, mock_cached_repository
    ):

        cached = await mock_cached_repository.save(sample_user_preference_entity)

        assert cached is not None
        assert isinstance(cached, UserPreferenceEntity)
        assert cached.email_enabled is True
        assert cached.telegram_enabled is False
        assert cached.telegram_id is None

    @pytest.mark.asyncio
    async def test_update_entity_to_cache(
        self, sample_user_preference_entity, mock_cached_repository
    ):

        cached = await mock_cached_repository.update(sample_user_preference_entity)

        assert cached is not None
        assert isinstance(cached, UserPreferenceEntity)
        assert cached.email_enabled is True
        assert cached.telegram_enabled is False
        assert cached.telegram_id is None

    @pytest.mark.asyncio
    async def test_get_by_id_raises_errors(
        self, full_mocked_cached_repository, sample_user_preference_entity
    ):

        full_mocked_cached_repository._original.get_by_id.side_effect = DataError("some")

        with pytest.raises(DataError):
            await full_mocked_cached_repository.get_by_id(sample_user_preference_entity.id)

        full_mocked_cached_repository._original.get_by_id.assert_called()
