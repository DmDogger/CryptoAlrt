"""Domain exceptions for portfolio tracker module."""

from typing import final


class DomainValidationError(Exception):
    """Wrapper for base Exc"""


@final
class PortfolioNotFound(Exception):
    """Raised when portfolio is not found in database."""

    ...


@final
class PortfolioAlreadyExists(Exception):
    """Raised when trying to create portfolio that already exists."""

    ...


@final
class PortfolioSavingError(Exception):
    """Raised when portfolio saving to database fails."""

    ...


@final
class InvalidWalletAddress(Exception):
    """Raised when wallet address format is invalid."""

    ...


@final
class AssetNotFound(Exception):
    """Raised when asset is not found in portfolio."""

    ...


@final
class InsufficientAssetAmount(Exception):
    """Raised when trying to sell more assets than available."""

    ...


@final
class AssetSavingError(Exception):
    """Raised when asset saving to database fails."""

    ...


@final
class InvalidAssetAmount(Exception):
    """Raised when asset amount is invalid (negative or zero)."""

    ...
