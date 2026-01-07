import uuid
from datetime import datetime

from sqlalchemy import Enum as SQLAlchemyEnum, String, DateTime, func
from sqlalchemy.dialects.postgresql.base import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from domain.enums.status import StatusEnum
from domain.enums.channel import ChannelEnum
from .base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    channel: Mapped[ChannelEnum] = mapped_column(SQLAlchemyEnum(ChannelEnum))
    idempotency_key: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True
    )
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    recipient: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[StatusEnum] = mapped_column(
        SQLAlchemyEnum(StatusEnum), nullable=False
    )
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
