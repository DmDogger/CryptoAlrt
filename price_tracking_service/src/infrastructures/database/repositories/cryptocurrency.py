from dataclasses import dataclass
from decimal import Decimal
from typing import final
from uuid import UUID

from structlog import getLogger

from sqlalchemy import select, desc
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.dtos.coingecko_object import CoinGeckoDTO
from application.interfaces.repositories import CryptocurrencyRepositoryProtocol
from domain.entities.cryptocurrency import CryptocurrencyEntity
from domain.exceptions import RepositoryError, CryptocurrencyNotFound
from infrastructures.database.mappers.cryptocurrency_db_mapper import CryptocurrencyDBMapper
from infrastructures.database.models.cryptocurrency import Cryptocurrency, CryptocurrencyPrice

logger = getLogger(__name__)

@final
@dataclass(frozen=True, slots=True, kw_only=True)
class SQLAlchemyCryptocurrencyRepository(CryptocurrencyRepositoryProtocol):
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

    async def get_cryptocoins_list_by_coingecko_id(
            self,
            coingecko_id: str
    ) -> list[CryptocurrencyEntity]:
        """Get list of cryptocurrencies by CoinGecko ID.
        
        Args:
            coingecko_id: CoinGecko identifier (e.g., "bitcoin", "ethereum").
        
        Returns:
            List of CryptocurrencyEntity objects, ordered by creation date (newest first).
            Returns empty list if no cryptocurrencies found.
        
        Raises:
            RepositoryError: If a database error occurs during retrieval.
        """
        try:
            stmt = (
                select(Cryptocurrency)
                .where(Cryptocurrency.coingecko_id == coingecko_id)
                .order_by(desc(Cryptocurrency.created_at))
            )
            result = await self.session.scalars(stmt)
            models = result.all()
            
            if not models:
                logger.info(f"[Not found]: No cryptocurrencies found with coingecko_id: {coingecko_id}")
                return []
            
            logger.info(f"[Success]: Found {len(models)} cryptocurrency(ies) with coingecko_id: {coingecko_id}")
            return [self._mapper.from_database_model(model) for model in models]
            
        except SQLAlchemyError as e:
            logger.error(f"[SQLAlchemyError]: Error retrieving cryptocurrencies by coingecko_id={coingecko_id}: {e}")
            raise RepositoryError(
                f"Error occurred while retrieving cryptocurrencies with coingecko_id: {coingecko_id}"
            )




    async def get_by_cryptocurrency_id(
        self,
        cryptocurrency_id: UUID,
    ) -> CryptocurrencyEntity | None:
        """
        Retrieves a cryptocurrency entity by its ID.

        Args:
            cryptocurrency_id: The UUID of the cryptocurrency to retrieve.

        Returns:
            CryptocurrencyEntity if found, None otherwise.

        Raises:
            RepositoryError: If a database error occurs during retrieval.
        """
        try:
            stmt = (
                select(Cryptocurrency)
                .where(Cryptocurrency.id == cryptocurrency_id)
            )
            result = await self.session.scalars(stmt)
            model = result.first()
            if model is None:
                return None
            return self._mapper.from_database_model(model)
        except SQLAlchemyError as e:
            logger.error(f"Error: {e}, ID: {cryptocurrency_id}")
            raise RepositoryError(f"Occurred error during retrieving cryptocurrency information with ID: {cryptocurrency_id}")

    async def get_cryptocurrency_by_symbol(self, symbol: str):
        try:
            stmt = (
                select(Cryptocurrency)
                .where(Cryptocurrency.symbol == symbol)
            )
            res = await self.session.scalars(stmt)
            result = res.first()

            if result is None:
                logger.error(f"[Not found]: Not found cryptocurrency with symbol: {symbol}")
                return None
            return self._mapper.from_database_model(result)

        except SQLAlchemyError as e:
            logger.error(f"[SQLAlchemyError]: Occurred error during retrieving from database {e}")
            raise RepositoryError(f"Database error occurred while retrieving crypto with symbol: {symbol}")

    async def get_last_price(self, cryptocurrency_id: str | UUID) -> Decimal | None:
        """
        Get the last known price for a cryptocurrency.

        Args:
            cryptocurrency_id: The UUID of the cryptocurrency.

        Returns:
            The last price as Decimal if found, None otherwise.

        Raises:
            RepositoryError: If a database error occurs.
        """
        try:
            stmt = (
                select(CryptocurrencyPrice.price_usd)
                .where(CryptocurrencyPrice.cryptocurrency_id == cryptocurrency_id)
                .order_by(desc(CryptocurrencyPrice.timestamp))
                .limit(1)
            )
            result = await self.session.scalars(stmt)
            logger.info(f"Successfully got last price by crypto id: {cryptocurrency_id}")
            return result.first()
        except SQLAlchemyError as e:
            logger.error(f"Unexpected SQLAlchemy Error: {e}, crypto-id: {cryptocurrency_id}")
            raise RepositoryError(f"Occurred error during retrieving of cryptocurrency price information")


    async def get_sorted_cryptocurrencies_by_created_at_time(
            self,
    ) -> list[CryptocurrencyEntity]:
        """
        Retrieves all cryptocurrencies sorted by creation time in ascending order.

        Returns:
            A list of CryptocurrencyEntity objects sorted by created_at.
            Returns an empty list if no cryptocurrencies are found.

        Raises:
            RepositoryError: If a database error occurs during retrieval.
        """
        try:
            stmt = (
                select(Cryptocurrency)
                .order_by(Cryptocurrency.created_at)
            )
            result = await self.session.scalars(stmt)
            models = result.all()
            return [self._mapper.from_database_model(model) for model in models]
        except SQLAlchemyError as e:
            logger.error(f"Error: {e}")
            raise RepositoryError("Occurred error during retrieving list of cryptocurrency information")


    async def save(
            self,
            cryptocurrency_entity: CryptocurrencyEntity
    ) -> None:
        """
        Saves a new cryptocurrency or updates an existing one in the database.

        Args:
            cryptocurrency_entity: The CryptocurrencyEntity to persist.

        Raises:
            RepositoryError: If a database error occurs during save.
        """
        try:
            model = self._mapper.to_database_model(cryptocurrency_entity)
            self.session.add(model)
            await self.session.commit()

        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"IntegrityError: {e}, entity: {cryptocurrency_entity}")
            raise RepositoryError(f"Occurred error during saving cryptocurrency information with ID: {cryptocurrency_entity.id}")

        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"SQLAlchemyError: {e}, entity: {cryptocurrency_entity}")
            raise RepositoryError(f"Occurred error during saving cryptocurrency information with ID: {cryptocurrency_entity.id}")

    async def save_price(
            self,
            cryptocurrency_id: UUID,
            price_data: CoinGeckoDTO
    ) -> None:
        """Save price for cryptocurrency aggregate.
        
        If cryptocurrency doesn't exist, it will be created first.
        
        Args:
            cryptocurrency_id: UUID of cryptocurrency (aggregate root).
            price_data: Price data from CoinGecko API.
        
        Raises:
            RepositoryError: If save operation fails.
        """
        try:
            crypto = await self.session.get(Cryptocurrency, cryptocurrency_id)
            if not crypto:
                logger.error(f"[Error]:Cryptocurrency {cryptocurrency_id} not found...")
                raise CryptocurrencyNotFound(f"Cryptocurrency {cryptocurrency_id} not found...")


            
            logger.info(f"[Info]: Saving price for cryptocurrency {cryptocurrency_id}")
            
            price_model = self._mapper.from_api_response_to_database_model(
                entity=price_data,
                cryptocurrency_id=cryptocurrency_id
            )
            
            self.session.add(price_model)
            await self.session.commit()
            
            logger.info(f"[Success]: Price saved for cryptocurrency {cryptocurrency_id}")
            added_obj = await self.session.get(Cryptocurrency, cryptocurrency_id)
            return self._mapper.from_database_model(added_obj)

        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"[IntegrityError]: {e}, cryptocurrency_id: {cryptocurrency_id}")
            raise RepositoryError(f"Failed to save price for {cryptocurrency_id}: integrity error")

        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"[SQLAlchemyError]: {e}, cryptocurrency_id: {cryptocurrency_id}")
            raise RepositoryError(f"Failed to save price for {cryptocurrency_id}: database error")

