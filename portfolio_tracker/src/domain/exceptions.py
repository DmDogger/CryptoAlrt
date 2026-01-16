"""Domain exceptions for portfolio tracker module."""

from typing import final


class DomainError(Exception):
    """"""


class DomainValidationError(DomainError):
    """Wrapper for base Exc"""


@final
class PortfolioNotFound(DomainError):
    """Raised when portfolio is not found in database."""

    ...


@final
class PortfolioAlreadyExists(DomainError):
    """Raised when trying to create portfolio that already exists."""

    ...


@final
class PortfolioSavingError(DomainError):
    """Raised when portfolio saving to database fails."""

    ...


@final
class InvalidWalletAddress(DomainError):
    """Raised when wallet address format is invalid."""

    ...


@final
class AssetNotFound(DomainError):
    """Raised when asset is not found in portfolio."""

    ...


@final
class InsufficientAssetAmount(DomainError):
    """Raised when trying to sell more assets than available."""

    ...


@final
class AssetSavingError(DomainError):
    """Raised when asset saving to database fails."""

    ...


@final
class InvalidAssetAmount(DomainError):
    """Raised when asset amount is invalid (negative or zero)."""

    ...


@final
class RepositoryError(DomainError):
    """Raised when repository/database operations fail."""

    ...
