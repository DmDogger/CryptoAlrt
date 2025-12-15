from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import final
from uuid import UUID, uuid4
import re

from ..exceptions import DomainValidationError
from ..value_objects.threshold import ThresholdValueObject


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class AlertEntity:
    """Alert entity for tracking cryptocurrency prices.
    
    Represents an immutable object containing information about an alert
    that triggers when a specified threshold price for a cryptocurrency is reached.
    
    Attributes:
        id: Unique identifier of the alert.
        email: User's email for sending notifications.
        cryptocurrency: Cryptocurrency symbol (e.g., BTC, ETH).
        threshold_price: Threshold price value as a value object.
        is_active: Alert activity flag.
        created_at: Alert creation date and time in UTC.
    """
    id: UUID
    email: str
    cryptocurrency: str
    threshold_price: ThresholdValueObject
    is_triggered: bool
    is_active: bool
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validates entity fields after initialization.
        
        Checks email correctness and cryptocurrency symbol length.
        
        Raises:
            DomainValidationError: If email has invalid format or
                cryptocurrency symbol has invalid length.
        """
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", self.email):
            raise DomainValidationError("Invalid email format")
        if len(self.cryptocurrency) < 3 or len(self.cryptocurrency) > 100:
            raise DomainValidationError("Cryptocurrency symbol must be between 3 and 100 characters")

    @classmethod
    def create(
        cls,
        email: str,
        cryptocurrency: str,
        threshold_price: Decimal,
        is_active: bool = True,
        is_triggered: bool = False,
    ) -> "AlertEntity":
        """Factory method for creating a new AlertEntity instance.

        Args:
            email: User's email for sending notifications.
            cryptocurrency: Cryptocurrency symbol (e.g., BTC, ETH).
            threshold_price: Threshold price value as Decimal.
            is_active: Alert activity flag (default is True).
            is_triggered: Alert trigger flag (default is False).

        Returns:
            New AlertEntity instance with auto-generated ID
            and current creation date.
            
        Raises:
            DomainValidationError: If invalid data is provided.
        """
        return cls(
            id=uuid4(),
            email=email,
            cryptocurrency=cryptocurrency,
            threshold_price=ThresholdValueObject(value=threshold_price),
            is_triggered=is_triggered,
            is_active=is_active,
            created_at=datetime.now(UTC),
        )

    def mark_as_triggered(self) -> AlertEntity:
        """Mark alert as triggered when threshold price is reached.
        
        Returns:
            New AlertEntity instance with is_triggered flag set to True.
        """
        return AlertEntity(
            id=self.id,
            email=self.email,
            cryptocurrency=self.cryptocurrency,
            threshold_price=self.threshold_price,
            is_triggered=True,
            is_active=self.is_active,
            created_at=self.created_at,
        )

    def reset_trigger(self) -> AlertEntity:
        """Reset alert trigger status back to not triggered.
        
        Used to prepare alert for monitoring again after it has been triggered.
        
        Returns:
            New AlertEntity instance with is_triggered flag set to False.
        """
        return AlertEntity(
            id=self.id,
            email=self.email,
            cryptocurrency=self.cryptocurrency,
            threshold_price=self.threshold_price,
            is_triggered=False,
            is_active=self.is_active,
            created_at=self.created_at
        )


    def update_threshold(
            self,
            threshold_price: Decimal | None = None
    ) -> "AlertEntity":
        """Updates the alert's threshold price.
        
        Args:
            threshold_price: New threshold price value. If None, 
                returns the current instance without changes.
        
        Returns:
            New AlertEntity instance with updated threshold price
            or current instance if threshold_price is None.
            
        Raises:
            DomainValidationError: If provided price is invalid.
        """
        if threshold_price is not None:
            return AlertEntity(
                id=self.id,
                email=self.email,
                cryptocurrency=self.cryptocurrency,
                threshold_price=ThresholdValueObject(value=threshold_price),
                is_active=self.is_active,
                is_triggered=False,
                created_at=self.created_at
            )
        return self

    def deactivate(self) -> "AlertEntity":
        """Deactivates the alert.
        
        Returns:
            New AlertEntity instance with is_active flag set to False.
        """
        return AlertEntity(
                id=self.id,
                email=self.email,
                cryptocurrency=self.cryptocurrency,
                threshold_price=self.threshold_price,
                is_triggered=False,
                is_active=False,
                created_at=self.created_at
        )

    def change_email(self, new_email: str) -> "AlertEntity":
        """Changes the user's email for the alert.
        
        Args:
            new_email: New user's email address.
        
        Returns:
            New AlertEntity instance with updated email.
            
        Raises:
            DomainValidationError: If new email has invalid format.
        """
        return AlertEntity(
                id=self.id,
                email=new_email,
                cryptocurrency=self.cryptocurrency,
                threshold_price=self.threshold_price,
                is_triggered=self.is_triggered,
                is_active=self.is_active,
                created_at=self.created_at
        )

    def change_cryptocurrency(self, new_cryptocurrency: str) -> "AlertEntity":
        """Changes the tracked cryptocurrency for the alert.
        
        Args:
            new_cryptocurrency: New cryptocurrency symbol (e.g., BTC, ETH).
        
        Returns:
            New AlertEntity instance with updated cryptocurrency symbol.
            
        Raises:
            DomainValidationError: If cryptocurrency symbol has invalid length.
        """
        return AlertEntity(
                id=self.id,
                email=self.email,
                cryptocurrency=new_cryptocurrency,
                threshold_price=self.threshold_price,
                is_triggered=self.is_triggered,
                is_active=self.is_active,
                created_at=self.created_at
        )




