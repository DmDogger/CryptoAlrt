from typing import final


@final
class DomainValidationError(Exception):
    """Raised when domain entity validation fails."""
    ...

class EmailSendingError(Exception):
    """ Raised when occur error during sending email """