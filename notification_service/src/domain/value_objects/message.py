from dataclasses import dataclass
from typing import final

from ..exceptions import DomainValidationError


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class MessageValueObject:
    """Value object representing a notification message.
    
    Attributes:
        text: Message text content (1-100 characters)
    """
    text: str

    def __post_init__(self):
        if not isinstance(self.text, str):
            raise DomainValidationError("Message text must be a string")
        if len(self.text) <= 0 or len(self.text) > 100:
            raise DomainValidationError("Message text length must be between 1 and 100 characters")

