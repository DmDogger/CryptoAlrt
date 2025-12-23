from uuid import UUID

from application.interfaces import NotificationRepositoryProtocol
from application.interfaces.repositories import PreferenceRepositoryProtocol
from domain.entities.notification import NotificationEntity
from domain.entities.user_preference import UserPreferenceEntity
from domain.enums.status import StatusEnum


class FakeRepository(NotificationRepositoryProtocol):
    def __init__(self, preferences):
        self._preferences = set(preferences)

    async def save(self, preference: NotificationEntity) -> NotificationEntity:
        self._preferences.add(preference)
        return preference

    async def get_by_id(self, notification_id: UUID) -> NotificationEntity | None:
        return next((p for p in self._preferences if p.id == notification_id), None)

    async def update(self, preference: NotificationEntity) -> NotificationEntity:
        # Удаляем старый объект с таким же ID, если он есть
        self._preferences = {p for p in self._preferences if p.id != preference.id}
        self._preferences.add(preference)
        return preference

    async def get_by_idempotency_key(
        self, idempotency_key: str
    ) -> NotificationEntity | None:
        return next(
            (
                p
                for p in self._preferences
                if p.idempotency_key.key == idempotency_key
            ),
            None,
        )

    async def get_by_status(self, status: StatusEnum) -> list[NotificationEntity]:
        return [p for p in self._preferences if p.status == status]


class FakeUserPreferenceRepository(PreferenceRepositoryProtocol):
    def __init__(self, preferences):
        self._preferences = set(preferences)

    async def save(self, preference: UserPreferenceEntity):
        self._preferences.add(preference)

    async def get_by_id(self, id_: int):
        return next(p for p in self._preferences if p.id == id_)

    async def update(self, preference: NotificationEntity):
        self._preferences.add(preference)

    async def get_by_email(self, email: str):
        return next((p for p in self._preferences if p.email == email), None)

    async def get_by_telegram_id(self, telegram_id: int):
        return next((p for p in self._preferences if p.telegram_id == telegram_id), None)



