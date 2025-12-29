
class InfrastructureError(Exception):
    """ Wrapper for base Exception class """

class WalletNotFoundError(InfrastructureError):
    """Raises when wallet not found in database """

class FailedToSaveWalletError(InfrastructureError):
    """ Raises when unable to save wallet to DB """

class FailedToUpdateWalletError(InfrastructureError):
    """ Raises when unable to update wallet to DB """

class NonceNotFoundError(InfrastructureError):
    """ Raises when nonce not found in database """

class FailedToSaveNonceError(InfrastructureError):
    """ Raises when unable to save nonce to DB """

class FailedToUpdateNonceError(InfrastructureError):
    """ Raises when unable to update nonce to DB """

class PublicationError(InfrastructureError):
    """ raises when occurred error during publication message to Kafka """