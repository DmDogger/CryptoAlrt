class InfrastructureError(Exception):
    """ """


class ValueTooLarge(InfrastructureError):
    """Raises when value too large for cache (more than 50 mb.)"""


class CacheSerializationFailed(InfrastructureError):
    """Raises when failed serialization"""
