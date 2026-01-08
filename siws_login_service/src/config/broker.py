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
    """

    bootstrap_servers: str = Field(default="localhost:9092", alias="KAFKA_BOOTSTRAP_SERVERS")
    wallet_logged_in: str = Field(default="wallet-logged-in", alias="WALLET_LOGGED_IN")


siws_broker_settings = BrokerSettings()
