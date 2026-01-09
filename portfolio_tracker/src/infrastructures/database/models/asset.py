from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import String, ForeignKey, Numeric, DateTime, func
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql.base import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructures.database.models.base import Base


class Asset(Base):
    __tablename__ = "assets"

    __table_args__ = (UniqueConstraint("wallet_address", "ticker", name="uq_asset_wallet_ticker"),)

    asset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
    )
    ticker: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("crypto_prices.cryptocurrency", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(30, 18),
        nullable=False,
    )
    wallet_address: Mapped[str] = mapped_column(
        String(200),
        ForeignKey("portfolio.wallet_address", onupdate="CASCADE", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    crypto_price: Mapped["CryptoPrice"] = relationship(
        "CryptoPrice",
        lazy="joined",
    )

    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio",
        back_populates="assets",
    )
