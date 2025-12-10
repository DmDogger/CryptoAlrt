from typing import final

@final
class DomainValidationError(Exception):
    """Raised when domain entity validation fails."""
    ...


@final
class RepositoryError(Exception):
    """Raised when repository operation fails."""
    ...


@final
class PublishError(Exception):
    """Raised when event publishing fails."""
    ...