from typing import final

from pydantic import Field
from pydantic_settings import BaseSettings


@final
class SMTPSettings(BaseSettings):
    """SMTP server configuration settings."""

    # Defaults are set to allow module import without environment variables.
    # Override via SMTP_* env vars in production.
    host: str = Field(default="localhost", description="SMTP server hostname")
    port: int = Field(default=1025, description="SMTP server port")
    username: str = Field(
        default="", description="SMTP authentication username (optional)"
    )
    password: str = Field(
        default="", description="SMTP authentication password (optional)"
    )
    use_tls: bool = Field(default=False, description="Whether to use TLS encryption")
    noreply_email: str = Field(
        default="noreply@cryptoalrt.io", description="Base email from sending"
    )

    model_config = {
        "env_prefix": "SMTP_",
        "case_sensitive": False,
    }


smtp_settings = SMTPSettings()
