from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from src.application.use_cases.send_request_use_case import SendRequestUseCase
from src.application.use_cases.verify_signature_use_case import VerifySignatureUseCase

router = APIRouter()


@router.post(
    "/request-signature",
    summary="Request SIWS signature message",
    responses={
        200: {"description": "Signature message generated successfully"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"},
    },
)
@inject
async def send_request(
    wallet_address: str,
    use_case: FromDishka[SendRequestUseCase],
):
    """Generate SIWS message for wallet authentication."""
    message = await use_case.execute(wallet_address)
    return {"message": message}


@router.post(
    "/verify-signature",
    summary="Verify wallet signature",
    responses={
        200: {"description": "Signature verified successfully"},
        400: {"description": "Bad request"},
        404: {"description": "Nonce not found"},
        500: {"description": "Internal server error"},
    },
)
@inject
async def verify_signature(
    signature: str,
    wallet_address: str,
    use_case: FromDishka[VerifySignatureUseCase],
):
    """Verify wallet signature and mark nonce as used."""
    verified_wallet_address = await use_case.execute(
        signature=signature,
        wallet_address=wallet_address,
    )
    return {
        "status": "success",
        "wallet_address": verified_wallet_address,
    }
