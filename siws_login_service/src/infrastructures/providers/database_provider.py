"""Database providers for Dishka dependency injection."""

from typing import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.engine.url import make_url

from src.application.interfaces.repositories import (
    NonceRepositoryProtocol,
    WalletRepositoryProtocol,
)
from src.config.database import db_settings
from src.infrastructures.database.mappers.nonce_mapper import NonceDBMapper
from src.infrastructures.database.mappers.wallet_mapper import WalletDBMapper
from src.infrastructures.database.mappers.wallet_session_mapper import (
    WalletSessionDBMapper,
)
from src.infrastructures.database.repositories.nonce_repository import (
    SQLAlchemyNonceRepository,
)
from src.infrastructures.database.repositories.wallet_repository import (
    SQLAlchemyWalletRepository,
)


class DatabaseProvider(Provider):
    """Provider for database-related dependencies."""

    @provide(scope=Scope.APP)
    def provide_db_engine(self) -> AsyncEngine:
        """Provide database engine instance."""
        return create_async_engine(str(make_url(db_settings.database_url)), echo=False)

    @provide(scope=Scope.APP)
    def provide_sessionmaker(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        """Provide sessionmaker instance."""
        return async_sessionmaker(engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def provide_db_session(
        self, sessionmaker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        """Provide database session for request scope."""
        async with sessionmaker() as session:
            yield session

    @provide(scope=Scope.APP)
    def provide_nonce_mapper(self) -> NonceDBMapper:
        """Provide NonceDBMapper instance."""
        return NonceDBMapper()

    @provide(scope=Scope.APP)
    def provide_wallet_mapper(self) -> WalletDBMapper:
        """Provide WalletDBMapper instance."""
        return WalletDBMapper()

    @provide(scope=Scope.APP)
    def provide_wallet_session_mapper(self) -> WalletSessionDBMapper:
        """Provide WalletSessionDBMapper instance."""
        return WalletSessionDBMapper()

    @provide(scope=Scope.REQUEST)
    def provide_nonce_repository(
        self,
        session: AsyncSession,
        mapper: NonceDBMapper,
    ) -> NonceRepositoryProtocol:
        """Provide SQLAlchemyNonceRepository instance."""
        return SQLAlchemyNonceRepository(_session=session, _mapper=mapper)

    @provide(scope=Scope.REQUEST)
    def provide_wallet_repository(
        self,
        session: AsyncSession,
        mapper: WalletDBMapper,
        wallet_session_mapper: WalletSessionDBMapper,
    ) -> WalletRepositoryProtocol:
        """Provide SQLAlchemyWalletRepository instance."""
        return SQLAlchemyWalletRepository(
            _session=session,
            _mapper=mapper,
            _wallet_session_mapper=wallet_session_mapper,
        )

    @provide(scope=Scope.REQUEST)
    def provide_sqlalchemy_nonce_repository(
        self,
        session: AsyncSession,
        mapper: NonceDBMapper,
    ) -> SQLAlchemyNonceRepository:
        """Provide SQLAlchemyNonceRepository instance (concrete type).

        This is needed for SignatureVerifier which requires the concrete type
        rather than the protocol.
        """
        return SQLAlchemyNonceRepository(_session=session, _mapper=mapper)

    @provide(scope=Scope.REQUEST)
    def provide_sqlalchemy_wallet_repository(
        self,
        session: AsyncSession,
        mapper: WalletDBMapper,
        wallet_session_mapper: WalletSessionDBMapper,
    ) -> SQLAlchemyWalletRepository:
        """Provide SQLAlchemyWalletRepository instance (concrete type).

        This is needed for TerminateSessionsUseCase which requires the concrete type
        rather than the protocol.
        """
        return SQLAlchemyWalletRepository(
            _session=session,
            _mapper=mapper,
            _wallet_session_mapper=wallet_session_mapper,
        )
