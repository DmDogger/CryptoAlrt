from decimal import Decimal
from typing import Any

from domain.value_objects.analytics_vo import AnalyticsValueObject


class AnalyticsDBMapper:
    @staticmethod
    def from_database(row: Any) -> "AnalyticsValueObject":
        return AnalyticsValueObject(
            ticker=row.ticker,
            position_value=row.position_value if hasattr(row, "position_value") else Decimal("0"),
            allocation=row.allocation if hasattr(row, "allocation") else Decimal("0"),
            port_change=row.port_change if hasattr(row, "port_change") else Decimal("0"),
            amount=row.amount if hasattr(row, "amount") else Decimal("0"),
            current_price=row.current_price if hasattr(row, "current_price") else Decimal("0"),
        )
