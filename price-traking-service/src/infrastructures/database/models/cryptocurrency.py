import uuid
from datetime import datetime

from sqlalchemy import UUID as PG_UUID, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Cryptocurrency(Base):
    """SQLAlchemy model for cryptocurrency data."""
    __tablename__ = 'cryptocurrency'

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
        default=uuid.uuid4
    )
    symbol: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    alerts: Mapped[list['Alert']] = relationship(
        'Alert',
        back_populates='cryptocurrency',
        cascade='all, delete-orphan'
    )

