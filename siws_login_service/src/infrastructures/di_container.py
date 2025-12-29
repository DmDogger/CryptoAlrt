"""Dishka container configuration."""

from dishka import AsyncContainer, make_async_container

from src.infrastructures.providers import (
    BrokerProvider,
    CryptoProvider,
    DatabaseProvider,
    UseCaseProvider,
)


def create_container() -> AsyncContainer:
    """Create and configure Dishka container with all providers."""
    return make_async_container(
        DatabaseProvider(),
        CryptoProvider(),
        BrokerProvider(),
        UseCaseProvider(),
    )
