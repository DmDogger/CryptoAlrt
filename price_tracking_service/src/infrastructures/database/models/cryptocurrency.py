import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import UUID as PG_UUID, String, DateTime, func, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Cryptocurrency(Base):
    """SQLAlchemy model for cryptocurrency data."""

    __tablename__ = "cryptocurrency"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
        default=uuid.uuid4,
    )
    symbol: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    coingecko_id: Mapped[str] = mapped_column(String(20), nullable=False)

    alerts: Mapped[list["Alert"]] = relationship(
        "Alert", back_populates="cryptocurrency", cascade="all, delete-orphan"
    )

    price_history: Mapped[list["CryptocurrencyPrice"]] = relationship(
        "CryptocurrencyPrice",
        back_populates="cryptocurrency",
        cascade="all, delete-orphan",
    )


class CryptocurrencyPrice(Base):
    """SQLAlchemy model for cryptocurrency price data in moment."""

    __tablename__ = "cryptocurrency_price"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        server_default=func.now(),
    )
    cryptocurrency_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("cryptocurrency.id")
    )
    price_usd: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    market_cap_usd: Mapped[Decimal | None] = mapped_column(Numeric(30, 2), nullable=True)
    total_volume_24h_usd: Mapped[Decimal | None] = mapped_column(Numeric(30, 2), nullable=True)

    high_24h: Mapped[Decimal | None] = mapped_column(Numeric(30, 2), nullable=True)
    low_24h: Mapped[Decimal | None] = mapped_column(Numeric(30, 2), nullable=True)

    price_change_24h: Mapped[Decimal | None] = mapped_column(Numeric(20, 8), nullable=True)
    price_change_percentage_24h: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 4), nullable=True
    )

    cryptocurrency: Mapped["Cryptocurrency"] = relationship(
        "Cryptocurrency", back_populates="price_history"
    )
