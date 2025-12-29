"""Mapper for converting between NonceEntity and Nonce database model."""

from dataclasses import dataclass
from typing import final

from src.domain.entities.nonce_entity import NonceEntity
from src.domain.value_objects.nonce_vo import NonceVO
from src.domain.value_objects.wallet_vo import WalletAddressVO
from src.infrastructures.database.models.nonce_model import Nonce


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class NonceDBMapper:
    """Mapper for converting between domain NonceEntity and database Nonce model.

    This mapper provides bidirectional conversion between the domain entity
    and the SQLAlchemy database model, ensuring proper data transformation
    including conversion of value objects (WalletAddressVO, NonceVO) to/from strings.
    """

    @staticmethod
    def to_database_model(entity: NonceEntity) -> Nonce:
        """Converts a NonceEntity domain entity to a Nonce database model.

        Args:
            entity: The NonceEntity domain entity to convert.

        Returns:
            A Nonce SQLAlchemy model instance with data from the entity.
        """
        return Nonce(
            uuid=entity.uuid,
            wallet_address=entity.wallet_address.value,
            nonce=entity.nonce.value,
            domain=entity.domain,
            statement=entity.statement,
            uri=entity.uri,
            version=entity.version,
            expiration_time=entity.expiration_time,
            used_at=entity.used_at,
            issued_at=entity.issued_at,
            chain_id=entity.chain_id,
        )

    @staticmethod
    def from_database_model(nonce: Nonce) -> NonceEntity:
        """Converts a Nonce database model to a NonceEntity domain entity.

        Args:
            nonce: The Nonce SQLAlchemy model instance to convert.

        Returns:
            A NonceEntity domain entity with data from the database model.
        """
        return NonceEntity(
            uuid=nonce.uuid,
            wallet_address=WalletAddressVO.from_string(nonce.wallet_address),
            nonce=NonceVO(value=nonce.nonce),
            domain=nonce.domain,
            statement=nonce.statement,
            uri=nonce.uri,
            version=nonce.version,
            expiration_time=nonce.expiration_time,
            used_at=nonce.used_at,
            issued_at=nonce.issued_at,
            chain_id=nonce.chain_id,
        )

    @staticmethod
    def to_dict(entity: NonceEntity) -> dict:
        """Converts a NonceEntity domain entity to a dictionary.

        Args:
            entity: The NonceEntity domain entity to convert.

        Returns:
            A dictionary representation of the NonceEntity.
        """
        expiration_time = (
            entity.expiration_time.replace(tzinfo=None)
            if entity.expiration_time and entity.expiration_time.tzinfo
            else entity.expiration_time
        )
        used_at = (
            entity.used_at.replace(tzinfo=None)
            if entity.used_at and entity.used_at.tzinfo
            else entity.used_at
        )
        issued_at = (
            entity.issued_at.replace(tzinfo=None)
            if entity.issued_at and entity.issued_at.tzinfo
            else entity.issued_at
        )

        return {
            "uuid": str(entity.uuid),
            "wallet_address": entity.wallet_address.value,
            "nonce": entity.nonce.value,
            "domain": entity.domain,
            "statement": entity.statement,
            "uri": entity.uri,
            "version": entity.version,
            "expiration_time": expiration_time,
            "used_at": used_at,
            "issued_at": issued_at,
            "chain_id": entity.chain_id,
        }