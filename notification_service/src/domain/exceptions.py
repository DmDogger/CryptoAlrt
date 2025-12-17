from typing import final


@final
class DomainValidationError(Exception):
    """Raised when domain entity validation fails."""
    ...

@final
class EmailSendingError(Exception):
    """ Raised when occur error during sending email """
    ...

@final
class KeyValidationError(Exception):
    """Raised when key validation fails."""
    ...
