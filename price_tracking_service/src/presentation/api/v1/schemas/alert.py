import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field


class AlertCreateRequest(BaseModel):
    email: EmailStr = Field(
        description="Email of user who created alert."
    )
    cryptocurrency_slug: str = Field(
        description="Cryptocurrency slug as on Coingecko"
    )
    threshold_price: Decimal = Field(
        ge=0,
        description="Threshold price"
    )

class AlertUpdateRequest(BaseModel):
    email: EmailStr | None = None
    cryptocurrency_slug: str | None = None
    threshold_price: Decimal | None = None
    is_active: bool | None = None


class AlertResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    cryptocurrency: str
    threshold_price: Decimal
    is_active: bool
    created_at: datetime



