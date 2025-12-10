from dataclasses import dataclass
from typing import final

from sqlalchemy.ext.asyncio import AsyncSession
from structlog import getLogger

from application.interfaces.repositories import AlertRepositoryProtocol
from infrastructures.database.mappers.cryptocurrency_db_mapper import CryptocurrencyDBMapper

logger = getLogger(__name__)

@final
@dataclass(frozen=True, slots=True, kw_only=True)
class SQLAlchemyAlertRepository(AlertRepositoryProtocol):
    """SQLAlchemy implementation of the Cryptocurrency Repository.

    This repository is responsible for database operations (CRUD) only.
    Mapping logic is delegated to CryptocurrencyDBMapper following SRP.
    """
    session: AsyncSession
    _mapper: CryptocurrencyDBMapper

    def __init__(
        self,
        session: AsyncSession,
        mapper: CryptocurrencyDBMapper,
    ) -> None:
        """
        Initialize the repository with database session and mapper.

        Args:
            session: The async SQLAlchemy session for database operations.
            mapper: The mapper for converting between entities and database models.
        """
        object.__setattr__(self, 'session', session)
        object.__setattr__(self, '_mapper', mapper)
