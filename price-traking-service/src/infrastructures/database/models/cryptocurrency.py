import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import UUID as PG_UUID, String, DateTime, func, ForeignKey, Numeric
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

    price_history: Mapped[list['CryptocurrencyPrice']] = relationship(
        'CryptocurrencyPrice',
        back_populates='cryptocurrency',
        cascade='all, delete-orphan'
    )


class CryptocurrencyPrice(Base):
    """SQLAlchemy model for cryptocurrency price data in moment."""

    __tablename__ = 'cryptocurrency_price'

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )
    cryptocurrency_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('cryptocurrency.id')
    )
    price: Mapped[Decimal] = mapped_column(Numeric(10,2), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    cryptocurrency: Mapped['Cryptocurrency'] = relationship(
        'Cryptocurrency',
        back_populates='price_history'
    )

