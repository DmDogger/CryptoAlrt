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

@final
class CryptocurrencyNotFound(Exception):
    """Raised when cryptocurrency not in database. """

@final
class AlertSavingError(Exception):
    """ Raised when this data already exists in database"""

@final
class UnsuccessfullyCoinGeckoAPICall(Exception):
    """ """

@final
class UnexpectedError(Exception):
    """ Raise when occurred unexpected error """

@final
class AlertNotFound(Exception):
    """ Raise when alert not found """