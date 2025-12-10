from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import final
from uuid import uuid4, UUID


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CryptocurrencyDTO:
    """Application DTO for transferring Cryptocurrency data between layers. """
    id: UUID = field(default_factory=uuid4)
    symbol: str
    name: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))