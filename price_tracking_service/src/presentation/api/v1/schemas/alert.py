import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field


class AlertCreateRequest(BaseModel):
    email: EmailStr = Field(
        description="Email of user who created alert."
    )
    telegram_id: int | None = Field(
        default=None,
        description="Telegram ID of user who created alert."
    )
    cryptocurrency_slug: str = Field(
        description="Cryptocurrency slug as on Coingecko"
    )
    threshold_price: Decimal = Field(
        ge=0,
        description="Threshold price"
    )
    is_active: bool = Field(default=True)

class AlertUpdateRequest(BaseModel):
    """Request model for updating an alert.

    Note: Cryptocurrency cannot be updated. To change the cryptocurrency,
    delete the alert and create a new one.
    """
    email: EmailStr | None = None
    telegram_id: int | None = None
    threshold_price: Decimal | None = None
    is_active: bool | None = None

class AlertDeleteRequest(BaseModel):
    email: str
    id: uuid.UUID


class AlertResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    telegram_id: int | None
    cryptocurrency: str
    threshold_price: Decimal
    is_triggered: bool
    is_active: bool
    created_at: datetime



