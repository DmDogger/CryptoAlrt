from src.presentation.api.v1.schemas.requests import (
    RequestSignatureRequest,
    VerifySignatureRequest,
)
from src.presentation.api.v1.schemas.responses import (
    RequestSignatureResponse,
    VerifySignatureResponse,
)


class AuthMapper:
    """Mapper for authentication request/response conversion."""

    @staticmethod
    def to_request_signature_dto(request: RequestSignatureRequest) -> str:
        """Convert Pydantic request to use case input.

        Args:
            request: RequestSignatureRequest from API.

        Returns:
            Wallet address string for use case.
        """
        return request.wallet_address

    @staticmethod
    def to_verify_signature_dto(
        request: VerifySignatureRequest,
    ) -> tuple[str, str]:
        """Convert Pydantic request to use case inputs.

        Args:
            request: VerifySignatureRequest from API.

        Returns:
            Tuple of (signature, wallet_address) for use case.
        """
        return request.signature, request.wallet_address

    @staticmethod
    def to_request_signature_response(message: str) -> RequestSignatureResponse:
        """Convert use case output to API response.

        Args:
            message: SIWS message string from use case.

        Returns:
            RequestSignatureResponse for API.
        """
        return RequestSignatureResponse(message=message)

    @staticmethod
    def to_verify_signature_response(wallet_address: str) -> VerifySignatureResponse:
        """Convert use case output to API response.

        Args:
            wallet_address: Verified wallet address from use case.

        Returns:
            VerifySignatureResponse for API.
        """
        return VerifySignatureResponse(
            status="success",
            wallet_address=wallet_address,
        )
