from domain.entities.user_preference import UserPreferenceEntity
from infrastructures.database.models.user_preference import UserPreference


class UserPreferenceDBMapper:
    @staticmethod
    def to_dict(entity: UserPreferenceEntity) -> dict:
        return {
            "id": str(entity.id),
            "email": entity.email,
            "email_enabled": entity.email_enabled,
            "telegram_id": entity.telegram_id,
            "telegram_enabled": entity.telegram_enabled,
        }

    @staticmethod
    def from_database_model(model: UserPreference) -> UserPreferenceEntity:
        return UserPreferenceEntity(
            id=model.id,
            email=model.email,
            email_enabled=model.email_enabled,
            telegram_id=model.telegram_id,
            telegram_enabled=model.telegram_enabled,
        )

    @staticmethod
    def to_database_model(entity: UserPreferenceEntity) -> UserPreference:
        return UserPreference(
            id=entity.id,
            email=entity.email,
            email_enabled=entity.email_enabled,
            telegram_id=entity.telegram_id,
            telegram_enabled=entity.telegram_enabled,
        )
