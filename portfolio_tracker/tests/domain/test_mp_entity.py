from decimal import Decimal

from domain.entities.mp_entity import MPEntity


class TestMPEntity:
    def test_entity_mp_creates_correct(self, sample_mp_entity: MPEntity):
        assert sample_mp_entity.price == Decimal("90_000")
        assert sample_mp_entity.name == "Bitcoin"
        assert sample_mp_entity.cryptocurrency == "BTC"

    def test_from_event_to_mp_correct(self, sample_price_updated_event):

        res = MPEntity.from_event(sample_price_updated_event)

        assert isinstance(res, MPEntity)
        assert res.price == Decimal("90_000")
        assert res.name == "Bitcoin"
