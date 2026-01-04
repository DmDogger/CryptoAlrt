
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

class TokenIssueError(InfrastructureError):
    """ raises when occurred error during issue token for subject """

class SessionError(InfrastructureError):
    """ Raises when occur error getting session """

class SessionSaveFailed(InfrastructureError):
    """Raises when occur error during save a new session """

class RevokeSessionError(InfrastructureError):
    """ Raises when failed to revoke session(s)"""