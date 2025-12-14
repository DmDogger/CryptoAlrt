from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine
from typing import AsyncIterable, Iterable
import httpx
from faststream.kafka import KafkaBroker

from application.use_cases.fetch_and_save_to_database import FetchAndSaveUseCase
from application.use_cases.check_threshold import CheckThresholdUseCase
from application.use_cases.get_alerts_list_by_email import GetAlertsUseCase
from application.use_cases.save_alert_to_database import SaveAlertToDBUseCase
from application.use_cases.publish_price_update_to_broker import PublishPriceUpdateToBrokerUseCase
from application.use_cases.process_price_update import ProcessPriceUpdateUseCase
from application.interfaces.repositories import AlertRepositoryProtocol, CryptocurrencyRepositoryProtocol
from application.interfaces.event_publisher import EventPublisherProtocol
from infrastructures.http.coingecko_client import CoinGeckoClient
from infrastructures.database.repositories.cryptocurrency import SQLAlchemyCryptocurrencyRepository
from infrastructures.database.repositories.alert import SQLAlchemyAlertRepository
from infrastructures.database.mappers.cryptocurrency_db_mapper import CryptocurrencyDBMapper
from infrastructures.database.mappers.alert_db_mapper import AlertDBMapper
from infrastructures.broker.publisher import KafkaEventPublisher
from presentation.api.v1.mappers.to_response import AlertPresentationMapper
from config.database import db_settings


class InfrastructureProvider(Provider):
    """Провайдер для инфраструктурного слоя."""
    
    @provide(scope=Scope.APP)
    async def get_http_client(self) -> AsyncIterable[httpx.AsyncClient]:
        """HTTP клиент для всего приложения."""
        client = httpx.AsyncClient(timeout=30.0)
        yield client
        await client.aclose()
    
    @provide(scope=Scope.APP)
    def get_db_engine(self) -> Iterable[AsyncEngine]:
        """Database engine."""
        engine = create_async_engine(
            db_settings.database_url,
            echo=False,
            pool_pre_ping=True,
        )
        yield engine
        engine.sync_engine.dispose()
    
    @provide(scope=Scope.APP)
    def get_session_factory(self, engine: AsyncEngine) -> async_sessionmaker:
        """Session factory."""
        return async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    
    @provide(scope=Scope.REQUEST)
    async def get_session(self, session_factory: async_sessionmaker) -> AsyncIterable[AsyncSession]:
        """Database session для каждого запроса."""
        async with session_factory() as session:
            yield session
    
    @provide(scope=Scope.REQUEST)
    def get_mapper(self) -> CryptocurrencyDBMapper:
        """Mapper для криптовалют."""
        return CryptocurrencyDBMapper()
    
    @provide(scope=Scope.REQUEST)
    def get_cryptocurrency_repository(
        self,
        session: AsyncSession,
        mapper: CryptocurrencyDBMapper
    ) -> CryptocurrencyRepositoryProtocol:
        """Repository для криптовалют."""
        return SQLAlchemyCryptocurrencyRepository(
            session=session,
            mapper=mapper
        )

    @provide(scope=Scope.REQUEST)
    def get_alert_repository(
        self,
        session: AsyncSession
    ) -> AlertRepositoryProtocol:
        """Repository для алертов."""
        return SQLAlchemyAlertRepository(
            session=session,
            mapper=AlertDBMapper()
        )
    
    @provide(scope=Scope.REQUEST)
    def get_coingecko_client(
        self,
        http_client: httpx.AsyncClient,
        repository: CryptocurrencyRepositoryProtocol
    ) -> CoinGeckoClient:
        """CoinGecko API клиент."""
        return CoinGeckoClient(
            client=http_client,
            cryptocurrency_repository=repository
        )

    @provide(scope=Scope.APP)
    def get_kafka_broker(self) -> KafkaBroker:
        """Kafka broker для FastStream."""
        from infrastructures.tasks.tasks import kafka_broker
        return kafka_broker

    @provide(scope=Scope.REQUEST)
    def get_event_publisher(self, kafka_broker: KafkaBroker) -> EventPublisherProtocol:
        """Event publisher для Kafka."""
        return KafkaEventPublisher(broker=kafka_broker)

    @provide(scope=Scope.REQUEST)
    def get_alert_presentation_mapper(self) -> AlertPresentationMapper:
        """Mapper для преобразования алертов."""
        return AlertPresentationMapper()


class UseCaseProvider(Provider):
    """Провайдер для use cases."""
    
    @provide(scope=Scope.REQUEST)
    def get_fetch_and_save_use_case(
        self,
        coingecko_client: CoinGeckoClient,
        repository: CryptocurrencyRepositoryProtocol
    ) -> FetchAndSaveUseCase:
        """Use case для получения и сохранения цен."""
        return FetchAndSaveUseCase(
            coingecko_client=coingecko_client,
            crypto_repository=repository
        )
    
    @provide(scope=Scope.REQUEST)
    def get_check_threshold_use_case(
        self,
        alert_repository: AlertRepositoryProtocol,
        event_publisher: EventPublisherProtocol,
    ) -> CheckThresholdUseCase:
        """Use case для проверки триггеров алертов."""
        return CheckThresholdUseCase(
            alert_repository=alert_repository,
            event_publisher=event_publisher
        )

    @provide(scope=Scope.REQUEST)
    def get_alerts_use_case(
        self,
        alert_repository: AlertRepositoryProtocol
    ) -> GetAlertsUseCase:
        """Use case для получения алертов по email."""
        return GetAlertsUseCase(
            repository=alert_repository
        )

    @provide(scope=Scope.REQUEST)
    def get_save_alert_use_case(
        self,
        alert_repository: AlertRepositoryProtocol,
        cryptocurrency_repository: CryptocurrencyRepositoryProtocol,
        mapper: AlertPresentationMapper
    ) -> SaveAlertToDBUseCase:
        """Use case для сохранения алерта в базу данных."""
        return SaveAlertToDBUseCase(
            alert_repository=alert_repository,
            cryptocurrency_repository=cryptocurrency_repository,
            mapper=mapper
        )

    @provide(scope=Scope.REQUEST)
    def get_publish_price_update_use_case(
        self,
        event_publisher: EventPublisherProtocol,
        cryptocurrency_repository: CryptocurrencyRepositoryProtocol
    ) -> PublishPriceUpdateToBrokerUseCase:
        """Use case для публикации обновлений цен в брокер."""
        return PublishPriceUpdateToBrokerUseCase(
            broker=event_publisher,
            repository=cryptocurrency_repository
        )

    @provide(scope=Scope.REQUEST)
    def get_process_price_update_use_case(
        self,
        fetch_and_save_use_case: FetchAndSaveUseCase,
        publish_price_update_use_case: PublishPriceUpdateToBrokerUseCase,
        check_threshold_use_case: CheckThresholdUseCase
    ) -> ProcessPriceUpdateUseCase:
        """Use case для полного процесса обновления цен."""
        return ProcessPriceUpdateUseCase(
            fetch_and_save_use_case=fetch_and_save_use_case,
            publish_price_updated_use_case=publish_price_update_use_case,
            check_threshold_use_case=check_threshold_use_case
        )
