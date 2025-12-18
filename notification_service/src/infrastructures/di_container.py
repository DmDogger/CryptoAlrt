from dishka import AsyncContainer, make_async_container

from infrastructures.providers import InfrastructureProvider, UseCaseProvider


def create_container() -> AsyncContainer:
    return make_async_container(
        InfrastructureProvider(),
        UseCaseProvider(),
    )


