
class InfrastructureError(Exception):
    """ Wrapper for base Exception class """

class WalletNotFoundError(InfrastructureError):
    """Raises when wallet not found in database """

class FailedToSaveWalletError(InfrastructureError):
    """ Raises when unable to save wallet to DB """

class FailedToUpdateWalletError(InfrastructureError):
    """ Raises when unable to update wallet to DB """
