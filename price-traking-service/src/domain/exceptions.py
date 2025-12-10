from typing import final

@final
class DomainValidationError(Exception):
    """Raised when domain entity validation fails."""
    ...