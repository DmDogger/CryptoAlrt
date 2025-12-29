from pydantic import BaseModel, Field


class RequestSignatureResponse(BaseModel):
    """Response schema for signature message."""

    message: str = Field(
        ...,
        description="SIWE message string ready for signing",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "cryptoalrt.io wants you to sign in with your Solana account:\n..."
            }
        }


class VerifySignatureResponse(BaseModel):
    """Response schema for signature verification."""

    status: str = Field(
        default="success",
        description="Verification status",
    )
    wallet_address: str = Field(
        ...,
        description="Verified wallet address",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "wallet_address": "5cRypRAdKEUtMCyFdqtEifWER5GMCfVnhZ8EUtcB7Sc3",
            }
        }