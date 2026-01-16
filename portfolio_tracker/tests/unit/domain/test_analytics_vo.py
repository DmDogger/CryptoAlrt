from decimal import Decimal
from typing import Any

from domain.value_objects.analytics_vo import AnalyticsValueObject
from infrastructures.database.mappers.analytics_db_mapper import AnalyticsDBMapper


class TestAnalyticsValueObject:
    def test_analytics_value_object_creation(self, sample_analytics_vo: AnalyticsValueObject):
        assert sample_analytics_vo.ticker == "BTC"
        assert sample_analytics_vo.port_change is None

    def test_analytics_db_mapper_from_database(self, row_obj: Any):

        analytics_vo = AnalyticsDBMapper.from_database(row_obj)

        assert analytics_vo.ticker == "BTC"
        assert analytics_vo.current_price == Decimal("50_000")
        assert isinstance(analytics_vo, AnalyticsValueObject)
