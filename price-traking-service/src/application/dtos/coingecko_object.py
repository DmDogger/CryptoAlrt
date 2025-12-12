from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import final
from uuid import uuid4

@final
@dataclass(frozen=True, slots=True)
class CoinGeckoDTO:
    id: str
    symbol: str
    name: str
    current_price: Decimal
    market_cap: Decimal | None
    total_volume: Decimal | None
    high_24h: Decimal | None
    low_24h: Decimal
    price_change_24h: Decimal | None
    price_change_percentage_24h: Decimal | None
    last_updated: datetime

    @classmethod
    def to_dto(cls, data: dict) -> "CoinGeckoDTO":
        return cls(
            id=str(data.get("id", uuid4())),
            symbol=data["symbol"],
            name=data["name"],
            current_price=data["current_price"],
            market_cap=data["market_cap"],
            total_volume=data["total_volume"],
            high_24h=data["high_24h"],
            low_24h=data["low_24h"],
            price_change_24h=data["price_change_24h"],
            price_change_percentage_24h=data["price_change_percentage_24h"],
            last_updated=data["last_updated"]
        )

    def to_dict(self, dto: "CoinGeckoDTO") -> dict:
        return {
            "id": dto.id,
            "symbol": dto.symbol,
            "name": dto.name,
            "current_price": dto.current_price,
            "market_cap": dto.market_cap,
            "total_volume": dto.total_volume,
            "high_24h": dto.high_24h,
            "low_24h": dto.low_24h,
            "price_change_24h": dto.price_change_24h,
            "price_change_percentage_24h": dto.price_change_percentage_24h,
            "last_updated": dto.last_updated
        }