from dishka import make_async_container, AsyncContainer
from infrastructures.providers import InfrastructureProvider, UseCaseProvider


def create_container() -> AsyncContainer:
    return make_async_container(
        InfrastructureProvider(),
        UseCaseProvider(),
    )
