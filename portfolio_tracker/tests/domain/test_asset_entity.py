from decimal import Decimal

import pytest

from domain.exceptions import DomainValidationError


class TestAssetEntity:
    def test_asset_entity_works_correct(self, sample_asset_entity):
        assert sample_asset_entity is not None
        assert sample_asset_entity.amount == Decimal("0.0005")
        assert sample_asset_entity.ticker == "BTC"

    def test_set_amount(self, sample_asset_entity):
        amounted = sample_asset_entity.set_amount(Decimal("1"))

        assert amounted.amount == Decimal("1")

    def test_negative_amount_raise_error(self, sample_asset_entity):
        with pytest.raises(DomainValidationError):
            sample_asset_entity.set_amount(Decimal("-1"))
