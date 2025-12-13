from abc import abstractmethod
from typing import Protocol, Any


class SerializationMapperProtocol(Protocol):
    """Protocol for serialization/deserialization of Application DTOs.

    This interface allows the Application layer to serialize DTOs
    without depending on Infrastructure implementations.
    """

    @abstractmethod
    def to_dict(self, dto: Any) -> dict:
        """
        Converts an Application DTO to a dictionary for serialization.
        """
        ...

    @abstractmethod
    def from_dict(self, data: dict) -> Any:
        """
        Converts a dictionary from deserialization back to an Application DTO.
        """
        ...