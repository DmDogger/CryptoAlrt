from pydantic import Field
from pydantic_settings import BaseSettings


class EventSettings(BaseSettings):
    event_email_changed: str = Field(
        default="event_email_changed", alias="EVENT_EMAIL_CHANGED"
    )

    event_crypto_changed: str = Field(
        default="event_crypto_changed", alias="EVENT_CRYPTO_CHANGED"
    )

    event_threshold_changed: str = Field(
        default="event_threshold_changed", alias="EVENT_THRESHOLD_CHANGED"
    )


event_settings = EventSettings()
