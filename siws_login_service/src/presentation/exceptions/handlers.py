"""Exception handlers for FastAPI application."""

import structlog
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.domain.exceptions import (
    DomainError,
    NonceNotFoundError as DomainNonceNotFoundError,
)
from src.infrastructures.exceptions import (
    InfrastructureError,
    WalletNotFoundError,
    SessionError,
    NonceNotFoundError as InfrastructureNonceNotFoundError,
)

logger = structlog.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers for the FastAPI application.

    Args:
        app: FastAPI application instance.
    """

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):
        """Handle domain validation errors."""
        logger.error(
            "Domain error occurred",
            error=str(exc),
            path=request.url.path,
        )
        return JSONResponse(
            status_code=400,
            content={"message": str(exc), "error_type": "Domain Error"},
        )

    @app.exception_handler(WalletNotFoundError)
    async def wallet_not_found_handler(request: Request, exc: WalletNotFoundError):
        """Handle wallet not found errors."""
        logger.warning(
            "Wallet not found",
            error=str(exc),
            path=request.url.path,
        )
        return JSONResponse(
            status_code=404,
            content={"message": str(exc), "error_type": "Wallet Not Found Error"},
        )

    @app.exception_handler(InfrastructureNonceNotFoundError)
    async def infrastructure_nonce_not_found_handler(
        request: Request, exc: InfrastructureNonceNotFoundError
    ):
        """Handle infrastructure nonce not found errors."""
        logger.warning(
            "Nonce not found (infrastructure)",
            error=str(exc),
            path=request.url.path,
        )
        return JSONResponse(
            status_code=404,
            content={"message": str(exc), "error_type": "NonceNotFoundError"},
        )

    @app.exception_handler(DomainNonceNotFoundError)
    async def domain_nonce_not_found_handler(request: Request, exc: DomainNonceNotFoundError):
        """Handle domain nonce not found errors."""
        logger.warning(
            "Nonce not found (domain)",
            error=str(exc),
            path=request.url.path,
        )
        return JSONResponse(
            status_code=404,
            content={"message": str(exc), "error_type": "NonceNotFoundError"},
        )

    @app.exception_handler(SessionError)
    async def session_error_handler(request: Request, exc: SessionError):
        """Handle session-related errors."""
        logger.error(
            "Session error occurred",
            error=str(exc),
            path=request.url.path,
        )
        return JSONResponse(
            status_code=400,
            content={"message": str(exc), "error_type": "SessionError"},
        )

    @app.exception_handler(InfrastructureError)
    async def infrastructure_error_handler(request: Request, exc: InfrastructureError):
        """Handle infrastructure errors."""
        logger.error(
            "Infrastructure error occurred",
            error=str(exc),
            path=request.url.path,
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal server error",
                "error_type": "InfrastructureError",
            },
        )
