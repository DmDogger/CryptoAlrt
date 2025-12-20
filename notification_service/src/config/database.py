from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration settings for notification_service."""

    # Keep a safe default that doesn't require env vars at import time.
    # Override via DB_DATABASE_URL in your environment/.env.
    database_url: str = "postgresql+asyncpg://dmitrii@localhost:5432/cryptoalrt"

    class Config:
        env_prefix = "DB_"
        env_file = ".env"


db_settings = DatabaseSettings()



