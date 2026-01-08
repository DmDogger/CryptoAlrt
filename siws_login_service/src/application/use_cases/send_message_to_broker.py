"""Use case for publishing wallet login events to Kafka.

Sends wallet logged-in events to message broker for downstream services.
"""
import structlog
from aiokafka.errors import (
    KafkaConnectionError,
    KafkaTimeoutError,
    KafkaConfigurationError,
    InvalidTopicError,
)

from src.application.interfaces.event_publisher import EventPublisherProtocol
from src.infrastructures.exceptions import PublicationError
from src.domain.events.wallet_logged_in_event import WalletLoggedInEvent
from src.domain.value_objects.wallet_vo import WalletAddressVO
from src.config.broker import siws_broker_settings

logger = structlog.getLogger(__name__)


class SendUserLoggedUseCase:
    """Use case for publishing wallet logged in event to message broker."""

    def __init__(
        self,
        broker: EventPublisherProtocol,
    ):
        """Initialize the use case with required dependencies.

        Args:
            broker: Event publisher for sending messages to broker.
        """
        self._broker = broker

    async def execute(
        self,
        wallet_address: str | WalletAddressVO,
    ) -> None:
        """Publish wallet logged in event to broker.

        Args:
            wallet_address: Wallet address as string or WalletAddressVO instance.

        Raises:
            PublicationError: If publishing fails.
        """
        try:
            if isinstance(wallet_address, str):
                wallet_address = WalletAddressVO.from_string(wallet_address)

            wallet_logged_in_event = WalletLoggedInEvent.create_event(
                pubkey=wallet_address,
            )

            logger.info(
                "Publishing wallet logged in event",
                topic=siws_broker_settings.wallet_logged_in,
            )
            await self._broker.publish(
                topic=siws_broker_settings.wallet_logged_in,
                event=wallet_logged_in_event,
            )
            logger.info("Wallet logged in event published successfully")

        except (KafkaConnectionError, KafkaTimeoutError) as e:
            logger.error(f"Occurred error during event publication. Type: Connection Error: {e}")
            raise PublicationError(f"Cannot to send message to broker #1") from e

        except KafkaConfigurationError as e:
            logger.error(f"Occurred error during event publication. Type: Configuration Error: {e}")
            raise PublicationError(f"Cannot to send message to broker #2") from e

        except InvalidTopicError as e:
            logger.error(f"Occurred error during event publication. Type: Topic Error: {e} ")
            raise PublicationError(f"Cannot to send message to broker #3") from e

        except Exception as e:
            logger.error(f"Occurred error during event publication. Type: Unknown: {e} ")
            raise PublicationError(f"Cannot to send message to broker #4") from e
