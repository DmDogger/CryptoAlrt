from pathlib import Path
from typing import final

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


@final
class JWTSettings(BaseSettings):
    """JWT configuration settings for token issuance.

    Loads JWT settings from environment variables or .env file.
    The secret key should be a PEM-formatted EdDSA private key.
    The public key is used for token verification.
    """

    secret_key: str = Field(alias="SIWS_PRIVATE_KEY")
    public_key: str = Field(alias="SIWS_PUBLIC_KEY")
    exp_time_mins: int = Field(default=59)

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )




jwt_settings = JWTSettings()
