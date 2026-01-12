class InfrastructureError(Exception):
    """"""


class DatabaseSavingError(InfrastructureError):
    """"""


class ValueTooLarge(InfrastructureError):
    """Cache value too large"""
