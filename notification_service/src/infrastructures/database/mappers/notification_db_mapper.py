from domain.enums.channel import ChannelEnum
from domain.enums.status import StatusEnum
from domain.entities.notification import NotificationEntity
from domain.value_objects.message import MessageValueObject
from domain.value_objects.idempotency_key import IdempotencyKeyVO
from infrastructures.database.models.notification import Notification


class NotificationDBMapper:
    @staticmethod
    def to_dict(dto: NotificationEntity) -> dict:
        created_at = (
            dto.created_at.replace(tzinfo=None)
            if dto.created_at and dto.created_at.tzinfo
            else dto.created_at
        )
        sent_at = (
            dto.sent_at.replace(tzinfo=None)
            if dto.sent_at and dto.sent_at.tzinfo
            else dto.sent_at
        )

        return {
            "id": str(dto.id),
            "channel": dto.channel.value,
            "message": dto.message.text,
            "recipient": dto.recipient,
            "idempotency_key": dto.idempotency_key.key,
            "status": dto.status.value,
            "sent_at": sent_at,
            "created_at": created_at,
        }

    @staticmethod
    def from_database_model(model: Notification) -> NotificationEntity:
        return NotificationEntity(
            id=model.id,
            channel=ChannelEnum(model.channel),
            message=MessageValueObject(text=model.message),
            recipient=model.recipient,
            idempotency_key=IdempotencyKeyVO(key=model.idempotency_key),
            status=StatusEnum(model.status),
            sent_at=model.sent_at,
            created_at=model.created_at,
        )

    @staticmethod
    def to_database_model(dto: NotificationEntity) -> Notification:
        created_at = (
            dto.created_at.replace(tzinfo=None)
            if dto.created_at and dto.created_at.tzinfo
            else dto.created_at
        )
        sent_at = (
            dto.sent_at.replace(tzinfo=None)
            if dto.sent_at and dto.sent_at.tzinfo
            else dto.sent_at
        )

        return Notification(
            id=dto.id,
            channel=dto.channel.value,
            message=dto.message.text,
            recipient=dto.recipient,
            idempotency_key=dto.idempotency_key.key,
            status=dto.status.value,
            sent_at=sent_at,
            created_at=created_at,
        )
