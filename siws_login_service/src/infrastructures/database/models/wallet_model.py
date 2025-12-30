"""SQLAlchemy database model for wallet data."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.dialects.postgresql.base import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructures.database.models.base import Base


class Wallet(Base):
    """SQLAlchemy model for wallet data.

    Represents a wallet entity in the database with information about
    the wallet address, activity timestamps, and creation time.

    Attributes:
        uuid: Unique identifier for the wallet (primary key).
        wallet_address: Base58-encoded wallet address string (unique, max 50 chars).
        last_active: Timestamp of the last activity/authentication for this wallet.
        created_at: Timestamp when the wallet entity was first created.
    """

    __tablename__ = "wallet"

    uuid: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        default=uuid4,
        primary_key=True,
        unique=True,
        nullable=False,
    )
    wallet_address: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )
    hashed_refresh_token: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=True,
        default=False,

    )
    last_active: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
