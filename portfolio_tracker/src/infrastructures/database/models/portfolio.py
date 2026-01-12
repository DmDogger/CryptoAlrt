from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, DateTime, Numeric, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructures.database.models.base import Base


class Portfolio(Base):
    __tablename__ = "portfolio"

    wallet_address: Mapped[str] = mapped_column(
        String(200),
        primary_key=True,
        unique=True,
        index=True,
    )

    total_value: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=True,
    )

    weight: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=True,
    )

    portfolio_total: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    assets_count: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    assets: Mapped[list["Asset"]] = relationship(
        "Asset",
        back_populates="portfolio",
        lazy="joined",
        cascade="all, delete-orphan",
    )
