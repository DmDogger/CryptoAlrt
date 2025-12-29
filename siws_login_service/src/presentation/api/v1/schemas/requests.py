from pydantic import BaseModel, Field


class RequestSignatureRequest(BaseModel):
    """Request schema for signature message generation."""

    wallet_address: str = Field(
        ...,
        description="Base58-encoded Solana wallet address",
        min_length=32,
        max_length=50,
    )

    class Config:
        json_schema_extra = {
            "example": {
                "wallet_address": "5cRypRAdKEUtMCyFdqtEifWER5GMCfVnhZ8EUtcB7Sc3"
            }
        }


class VerifySignatureRequest(BaseModel):
    """Request schema for signature verification."""

    wallet_address: str = Field(
        ...,
        description="Base58-encoded Solana wallet address",
        min_length=32,
        max_length=50,
    )
    signature: str = Field(
        ...,
        description="Base58-encoded Ed25519 signature",
        min_length=64,
    )

    class Config:
        json_schema_extra = {
            "example": {
                "wallet_address": "5cRypRAdKEUtMCyFdqtEifWER5GMCfVnhZ8EUtcB7Sc3",
                "signature": "base58_encoded_signature_here...",
            }
        }