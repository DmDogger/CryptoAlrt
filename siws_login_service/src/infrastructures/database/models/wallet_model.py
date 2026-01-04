"""SQLAlchemy database model for wallet data."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, ForeignKey, Integer, Boolean
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
    last_active: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class WalletSession(Base):
    """SQLAlchemy model for wallet session data.

    Represents a wallet session entity in the database with information about
    the wallet address, device identifier, refresh token hash, revocation status,
    and session creation time.

    The model uses a composite primary key consisting of wallet_address and device_id,
    allowing multiple sessions per wallet (one per device).

    Attributes:
        wallet_address: Base58-encoded wallet address string (foreign key to wallet table,
                       part of composite primary key, max 50 chars).
        refresh_token_hash: Hashed refresh token string (max 500 chars).
        device_id: Device identifier (part of composite primary key, integer).
        is_revoked: Session revocation flag (default: False).
        created_at: Timestamp when the wallet session was created.
    """

    __tablename__ = "wallet_sessions"

    wallet_address: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("wallet.wallet_address"),
        primary_key=True,
        index=True,
        nullable=False,
    )
    refresh_token_hash: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    device_id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        index=True,
        nullable=False,
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )