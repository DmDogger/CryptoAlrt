"""SQLAlchemy database model for nonce data."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql.base import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from infrastructures.database.models.base import Base


class Nonce(Base):
    """SQLAlchemy model for nonce data.

    Represents a nonce entity in the database with information about
    SIWE authentication session, including nonce value, wallet address,
    domain, timing information, and usage status.

    Attributes:
        uuid: Unique identifier for the nonce record (primary key).
        wallet_address: Base58-encoded wallet address string (foreign key to wallet table).
        nonce: Randomized token string used to prevent replay attacks (at least 8 chars).
        domain: RFC 4501 DNS authority that is requesting the signing.
        statement: Human-readable ASCII assertion that the user will sign (optional).
        uri: RFC 3986 URI referring to the resource that is the subject of the signing.
        version: Current version of the message (optional).
        expiration_time: ISO 8601 datetime indicating when the signed message expires.
        used_at: Timestamp when the nonce was used, None if not yet used (optional).
        issued_at: ISO 8601 datetime of the current time when the message was issued.
        chain_id: Chain ID to which the session is bound (default: "mainnet-beta").
    """

    __tablename__ = "nonce"

    uuid: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        unique=True,
        primary_key=True,
        nullable=False,
    )
    wallet_address: Mapped[str] = mapped_column(
        String(50),
        ForeignKey(
            "wallet.wallet_address",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    nonce: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    domain: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    statement: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        default=None,
    )
    uri: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    version: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        default=None,
    )
    expiration_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    chain_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="mainnet-beta",
    )
