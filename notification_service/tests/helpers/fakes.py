from application.interfaces import NotificationRepositoryProtocol
from application.interfaces.repositories import PreferenceRepositoryProtocol
from domain.entities.notification import NotificationEntity

from domain.entities.user_preference import UserPreferenceEntity


class FakeRepository(NotificationRepositoryProtocol):
    def __init__(self, preferences):
        self._preferences = set(preferences)

    async def save(self, preference: NotificationEntity):
        self._preferences.add(preference)

    async def get_by_id(self, id_: int):
        return next(p for p in self._preferences if p.id == id_)

    async def update(self, preference: NotificationEntity):
        self._preferences.add(preference)

    async def get_by_idempotency_key(self): ...

    async def get_by_status(self): ...