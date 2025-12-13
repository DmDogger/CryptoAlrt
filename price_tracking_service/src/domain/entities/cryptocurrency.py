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
