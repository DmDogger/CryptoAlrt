from domain.enums.channel import ChannelEnum

from ...domain.enums.status import StatusEnum
from ...domain.entities.notification import NotificationEntity
from ...domain.value_objects.message import MessageValueObject
from ...infrastructures.database.models.notification import Notification


class NotificationDBMapper:
    @staticmethod
    def to_dict(dto: NotificationEntity) -> dict:
        return {
            "id": str(dto.id),
            "channel": dto.channel.value,
            "message": dto.message.text,
            "recipient": dto.recipient,
            "source": dto.source,
            "idempotency_key": dto.idempotency_key,
            "status": dto.status.value,
            "attempts": dto.attempts,
            "last_error": dto.last_error,
            "sent_at": dto.sent_at,
            "created_at": dto.created_at,
        }

    @staticmethod
    def from_database_model(model: Notification) -> NotificationEntity:
        return NotificationEntity(
            id=model.id,
            channel=ChannelEnum(model.channel),
            message=MessageValueObject(text=model.message),
            recipient=model.recipient,
            source=model.source,
            idempotency_key=model.idempotency_key,
            status=StatusEnum(model.status),
            sent_at=model.sent_at,
            created_at=model.created_at,
        )

    @staticmethod
    def to_database_model(dto: NotificationEntity) -> Notification:
        return Notification(
            id=dto.id,
            channel=dto.channel.value,   # ← enum → str
            message=dto.message.text,    # ← VO → str
            recipient=dto.recipient,
            source=dto.source,
            idempotency_key=dto.idempotency_key,  # ← Добавь
            status=dto.status.value,     # ← enum → str
            attempts=dto.attempts,       # ← Добавь
            last_error=dto.last_error,   # ← Добавь
            sent_at=dto.sent_at,
            created_at=dto.created_at,
        )