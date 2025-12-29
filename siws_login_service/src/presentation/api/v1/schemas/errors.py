from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Error type/class name")
    details: dict[str, Any] | None = Field(
        None, description="Additional error details"
    )
