from pydantic import BaseModel


class AlertTriggeredDTO(BaseModel):
    id: str
    email: str
    telegram_id: str | None = None
    alert_id: str
    cryptocurrency: str
    threshold_price: str
    created_at: str
    current_price: str
    channel: str = "email"
