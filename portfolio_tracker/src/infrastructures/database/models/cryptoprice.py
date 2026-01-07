from datetime import datetime
from decimal import Decimal
from uuid import uuid4, UUID

from sqlalchemy import String, Numeric, DateTime, func, ForeignKey, Index
from sqlalchemy.dialects.postgresql.base import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructures.database.models.base import Base


class CryptoPrice(Base):
    __tablename__ = "crypto_prices"

    cryptocurrency: Mapped[str] = mapped_column(
        String(10),
        primary_key=True,
        nullable=False,
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    price_history: Mapped[list["MarketPriceHistory"]] = relationship(
        "MarketPriceHistory",
        back_populates="crypto_price",
        lazy="select",
        cascade="all, delete-orphan",
    )


class MarketPriceHistory(Base):
    """SQLAlchemy model for cryptocurrency price history."""

    __tablename__ = "crypto_price_history"

    __table_args__ = (Index("idx_crypto_timestamp", "cryptocurrency", "timestamp"),)

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    cryptocurrency: Mapped[str] = mapped_column(
        String(10),
        ForeignKey(
            "crypto_prices.cryptocurrency", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    crypto_price: Mapped["CryptoPrice"] = relationship(
        "CryptoPrice",
        back_populates="price_history",
        lazy="select",
    )
