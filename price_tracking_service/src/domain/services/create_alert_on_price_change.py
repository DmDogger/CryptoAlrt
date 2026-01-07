from datetime import datetime, UTC
from decimal import Decimal
from uuid import uuid4, UUID

from domain.events.alert_created import AlertCreatedEvent
from domain.value_objects.price import PriceValueObject


class CreateAlertOnPriceChangeService:
    """Service for creating alerts on cryptocurrency price changes.

    Checks if the percentage price change exceeds the specified threshold
    and creates an AlertCreatedEvent if necessary.
    """

    def __init__(self, price_value_object: PriceValueObject):
        self._price_value_object = price_value_object

    def create_alert_on_price_change(
        self,
        cryptocurrency_id: UUID,
        user_email: str,
        old_price: Decimal,
        new_price: Decimal,
        threshold_percent: Decimal,
        threshold_price: Decimal,
    ) -> AlertCreatedEvent | None:
        """Creates an alert if the percentage price change exceeds the threshold.

        Args:
            cryptocurrency_id: The cryptocurrency ID.
            user_email: The user's email for the alert.
            old_price: The old price.
            new_price: The new price.
            threshold_percent: The threshold for price change in percent.
            threshold_price: The price threshold (for future use).

        Returns:
            AlertCreatedEvent if alert is created, otherwise None.
        """
        percent_between = self._price_value_object.calculate_change_price_percent_(
            old_price=old_price,
            new_price=new_price,
        )
        if abs(percent_between) > threshold_percent:
            return AlertCreatedEvent(
                alert_id=uuid4(),
                email=user_email,
                cryptocurrency_id=cryptocurrency_id,
                threshold_price=threshold_price,
                price_change_percent=percent_between,
                current_price=new_price,
                timestamp=datetime.now(UTC),
            )
        return None
