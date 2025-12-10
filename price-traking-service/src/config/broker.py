from typing import final

from pydantic import Field
from pydantic_settings import BaseSettings


@final
class BrokerSettings(BaseSettings):
    """
    Kafka broker configuration settings.

    Attributes:
        bootstrap_servers (str): Kafka bootstrap servers (comma-separated).
            Example: "localhost:9092" or "kafka1:9092,kafka2:9092"
        price_updates_topic (str): Topic name for price update events.
        alert_created_topic (str): Topic name for alert creation events.
        publish_retries (int): Number of retries for publishing operations.
        publish_retry_backoff (float): Backoff factor for publish retries.
    """

    bootstrap_servers: str = Field(
        default="localhost:9092",
        alias="KAFKA_BOOTSTRAP_SERVERS"
    )
    price_updates_topic: str = Field(
        default="price-updates",
        alias="KAFKA_PRICE_UPDATES_TOPIC"
    )
    alert_created_topic: str = Field(
        default="alert-created",
        alias="KAFKA_ALERT_CREATED_TOPIC"
    )
    publish_retries: int = Field(
        default=3,
        alias="KAFKA_PUBLISH_RETRIES"
    )
    publish_retry_backoff: float = Field(
        default=0.5,
        alias="KAFKA_PUBLISH_RETRY_BACKOFF"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"