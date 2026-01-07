import uuid

from sqlalchemy import String, Boolean, BigInteger
from sqlalchemy.dialects.postgresql.base import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from infrastructures.database.models.base import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
    )
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=True, unique=True)
    telegram_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=True
    )
