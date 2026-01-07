"""Main application entry point for SIWS login service."""

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dishka.integrations.fastapi import setup_dishka

from src.config.cors import CORSSettings
from src.infrastructures.di_container import create_container
from src.presentation.api.v1.controllers.siws import router as siws_router
from src.presentation.exceptions import register_exception_handlers

logger = structlog.getLogger(__name__)

container = create_container()
cors_settings = CORSSettings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SIWS login service...")
    yield
    logger.info("Shutting down SIWS login service...")


app = FastAPI(
    title="SIWS Login Service",
    description="Sign-In With Solana authentication service",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_settings.cors_origins,
    allow_credentials=cors_settings.cors_allow_credentials,
    allow_methods=cors_settings.cors_allow_methods,
    allow_headers=cors_settings.cors_allow_headers,
)

setup_dishka(container, app)
app.include_router(siws_router, prefix="/api/v1", tags=["SIWS"])

register_exception_handlers(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
