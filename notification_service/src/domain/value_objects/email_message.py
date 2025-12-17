from dataclasses import dataclass
from typing import final

from ..exceptions import DomainValidationError


@final
@dataclass(frozen=True, slots=True)
class EmailMessage:
    """Value object representing an email message.
    
    Attributes:
        to: Recipient email address.
        subject: Email subject line.
        body: Email body content.
        from_address: Sender email address (optional, can be set by email client).
    """
    to: str
    subject: str
    body: str
    from_address: str | None = None

    def __post_init__(self):
        if not isinstance(self.to, str) or not self.to:
            raise DomainValidationError("Recipient email address must be a non-empty string")
        if not isinstance(self.subject, str) or not self.subject:
            raise DomainValidationError("Email subject must be a non-empty string")
        if not isinstance(self.body, str) or not self.body:
            raise DomainValidationError("Email body must be a non-empty string")
        if self.from_address is not None and (not isinstance(self.from_address, str) or not self.from_address):
            raise DomainValidationError("From address must be a non-empty string if provided")
