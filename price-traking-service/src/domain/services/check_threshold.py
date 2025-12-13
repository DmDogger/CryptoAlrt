from decimal import Decimal

from domain.entities.alert import AlertEntity


class CheckThresholdService:
    """Service for checking if a price exceeds the alert threshold.
    
    This domain service encapsulates the business logic for determining
    whether a given cryptocurrency price has reached or exceeded the
    threshold defined in an alert.
    """
    
    def __init__(
            self,
            alert_entity: AlertEntity
    ):
        """Initialize the service with an alert entity.
        
        Args:
            alert_entity: The alert entity containing the threshold to check against.
        """
        self._alert_entity = alert_entity

    def check_threshold(
            self,
            price_to_check: Decimal,
    ) -> bool:
        """Check if the given price meets or exceeds the alert threshold.
        
        Args:
            price_to_check: The current price to check against the threshold.
        
        Returns:
            True if the price meets or exceeds the threshold, False otherwise.
        """
        return self._alert_entity.threshold_price <= price_to_check
