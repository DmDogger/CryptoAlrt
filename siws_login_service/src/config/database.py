from typing import final

from pydantic_settings import BaseSettings


@final
class DatabaseSettings(BaseSettings):
    """Database configuration settings for siws_login_service."""

    database_url: str = "postgresql+asyncpg://dmitrii@localhost:5432/cryptoalrt"

    class Config:
        env_prefix = "DB_"
        env_file = ".env"
        extra = "ignore"


db_settings = DatabaseSettings()
