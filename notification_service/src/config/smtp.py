from typing import final

from pydantic import Field
from pydantic_settings import BaseSettings


@final
class SMTPSettings(BaseSettings):
    """SMTP server configuration settings."""
    
    host: str = Field(..., description="SMTP server hostname")
    port: int = Field(..., description="SMTP server port")
    username: str = Field(..., description="SMTP authentication username")
    password: str = Field(..., description="SMTP authentication password")
    use_tls: bool = Field(default=True, description="Whether to use TLS encryption")
    noreply_email: str = Field(..., description="Base email from sending")
    
    model_config = {
        "env_prefix": "SMTP_",
        "case_sensitive": False,
    }


smtp_settings = SMTPSettings()
