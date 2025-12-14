from decimal import Decimal

from domain.entities.alert import AlertEntity


class CheckThresholdService:
    """Domain service for checking if a cryptocurrency price meets the alert threshold.
    
    This service encapsulates the business logic for determining whether
    a given price has reached or exceeded the threshold defined in an alert entity.
    Implemented as a stateless service with static methods.
    """
    
    @staticmethod
    def check_threshold(
            alert_entity: AlertEntity,
            price_to_check: Decimal,
    ) -> bool:
        """Check if the given price meets or exceeds the alert threshold.
        
        Args:
            alert_entity: The alert entity containing the threshold to check against.
            price_to_check: The current cryptocurrency price to compare with the threshold.
        
        Returns:
            True if the price meets or exceeds the threshold, False otherwise.
        """
        return alert_entity.threshold_price <= price_to_check
