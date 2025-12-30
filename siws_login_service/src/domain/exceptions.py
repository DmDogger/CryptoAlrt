
class DomainError(Exception):
    """Wrapper for abase Exception class"""

class SignatureVerificationFailed(DomainError):
    """Raised when signature verification fails during authentication."""

class SignatureValidationError(DomainError):
    """Raised when the signature value fails validation, such as incorrect length or format."""

class InvalidWalletAddressError(DomainError):
    """Raised when the provided wallet address is invalid or malformed."""

class InvalidNonceError(DomainError):
    """Raised when the provided nonce is invalid or does not match the expected format."""

class NonceExpiredError(DomainError):
    """Raised when the nonce has expired and can no longer be used for authentication."""

class NonceValidationError(DomainError):
    """Raised when the nonce value fails validation, such as being too short or empty."""

class NonceAlreadyUsedError(DomainError):
    """Raised when the nonce has already been used and cannot be reused."""

class NonceNotFoundError(DomainError):
    """Raised when the requested nonce is not found in the system."""

class InvalidSignatureFormat(DomainError):
    """Raised when the signature format is invalid or does not match the expected structure."""

class DateValidationError(DomainError):
    """Raised when time after > time before"""

class TokenValidationError(DomainError):
    """"""


