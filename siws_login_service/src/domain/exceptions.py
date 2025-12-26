
class DomainError(Exception):
    """Wrapper for abase Exception class"""

class SignatureVerificationFailed(DomainError):
    """Raised when signature verification fails during authentication."""

class InvalidWalletAddressError(DomainError):
    """Raised when the provided wallet address is invalid or malformed."""

class InvalidNonceError(DomainError):
    """Raised when the provided nonce is invalid or does not match the expected format."""

class NonceExpiredError(DomainError):
    """Raised when the nonce has expired and can no longer be used for authentication."""

class NonceAlreadyUserError(DomainError):
    """Raised when the nonce has already been used and cannot be reused."""

class NonceNotFoundError(DomainError):
    """Raised when the requested nonce is not found in the system."""

class InvalidSignatureFormat(DomainError):
    """Raised when the signature format is invalid or does not match the expected structure."""

class DateValidationError(DomainError):
    """Raised when time after > time before"""

