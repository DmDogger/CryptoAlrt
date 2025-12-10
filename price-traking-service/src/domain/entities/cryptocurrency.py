from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import final
from uuid import UUID, uuid4
import re

from ..exceptions import DomainValidationError


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CryptocurrencyEntity:
    """Entity representing a cryptocurrency with identity."""
    id: UUID = field(default_factory=uuid4)
    symbol: str
    name: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not re.match(r"^[A-Z0-9]{3,10}$", self.symbol):
            raise DomainValidationError("Symbol must be 3-10 uppercase letters/numbers")
        if not self.name or len(self.name) < 2:
            raise DomainValidationError("Name must be at least 2 characters")

    @classmethod
    def create(cls, symbol: str, name: str) -> "Cryptocurrency":
        """Factory method to create a new cryptocurrency."""
        return cls(symbol=symbol.upper(), name=name.strip())

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "symbol": self.symbol,
            "name": self.name,
            "created_at": self.created_at.isoformat()
        }