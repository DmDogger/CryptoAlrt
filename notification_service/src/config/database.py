from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration settings for notification_service."""

    database_url: str = "postgresql+asyncpg://dmitrii@localhost:5432/cryptoalrt"

    class Config:
        env_prefix = "DB_"
        env_file = ".env"


db_settings = DatabaseSettings()








