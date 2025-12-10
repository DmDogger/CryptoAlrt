import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import UUID as PG_UUID, String, DateTime, func, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Alert(Base):
    """SQLAlchemy model for Alert data."""
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    cryptocurrency_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('cryptocurrency.id'),
        nullable=False
    )
    threshold_price: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    condition: Mapped[str] = mapped_column(String(10), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    cryptocurrency: Mapped['Cryptocurrency'] = relationship(
        'Cryptocurrency',
        back_populates='alerts'
    )
