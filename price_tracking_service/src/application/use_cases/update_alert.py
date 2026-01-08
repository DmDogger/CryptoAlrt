"""Use case for updating existing alert.

Updates alert fields (email, threshold price, active status) and publishes change events to Kafka.
"""

import uuid
from decimal import Decimal

import structlog
from sqlalchemy.exc import SQLAlchemyError

from application.interfaces.event_publisher import EventPublisherProtocol
from application.interfaces.repositories import AlertRepositoryProtocol
from config.broker import broker_settings
from domain.entities.alert import AlertEntity
from domain.events.alert_updated import AlertUpdatedEvent
from domain.exceptions import RepositoryError, DomainValidationError, AlertNotFound
from presentation.api.v1.mappers.to_response import AlertPresentationMapper
from presentation.api.v1.schemas.alert import AlertUpdateRequest

logger = structlog.getLogger(__name__)


class UpdateAlertUseCase:
    """Use case for updating alert fields (email, threshold_price, is_active).

    Handles partial updates of existing alerts. Retrieves alert by ID, merges
    changes from request into entity, persists updates, and publishes events
    for each changed field to Kafka.

    Note: Cryptocurrency cannot be updated - requires alert deletion and recreation.
    """

    def __init__(
        self,
        repository: AlertRepositoryProtocol,
        broker: EventPublisherProtocol,
        mapper: AlertPresentationMapper,
    ):

        self._repository = repository
        self._broker = broker
        self._mapper = mapper

    async def execute(
        self,
        alert_to_update: AlertUpdateRequest,
        alert_id: uuid.UUID,
    ) -> AlertEntity:
        """Update alert with provided fields and publish change events.

        Merges non-None fields from request into existing alert, saves to database,
        and publishes AlertUpdatedEvent for each changed field to Kafka.

        Args:
            alert_to_update: Partial update data (email, threshold_price, is_active).
            alert_id: UUID of alert to update.

        Returns:
            Updated AlertEntity with all fields populated.

        Raises:
            AlertNotFound: Alert with given ID not found.
            RepositoryError: Database operation failed.
            DomainValidationError: Domain validation failed (e.g., invalid email).
        """
        try:
            alert = await self._repository.get_alert_by_id(alert_id)

            if not alert:
                logger.error("Alert not found during update", alert_id=str(alert_id))
                raise AlertNotFound(f"Alert with ID {alert_id} not found")

            model = self._mapper.merge_update_from_pydantic_to_entity(
                existing=alert, pydantic_model=alert_to_update
            )

            old_email = alert.email
            old_crypto_symbol = alert.cryptocurrency
            old_threshold_price = alert.threshold_price.value
            logger.info(
                "Found existing alert values",
                alert_id=str(alert_id),
                old_email=old_email,
                old_crypto_symbol=old_crypto_symbol,
                old_threshold_price=str(old_threshold_price),
            )

            logger.info(
                "Starting alert update operation",
                alert_id=str(alert_id),
                email=alert.email,
                cryptocurrency=str(alert.cryptocurrency),
                threshold_price=str(alert.threshold_price.value),
                is_active=alert.is_active,
            )

            events: list[AlertUpdatedEvent] = []

            if model.email:
                logger.info("Changing email", old=old_email, new=model.email)
                event = AlertUpdatedEvent.on_email_change(
                    alert_id=model.id,
                    email=old_email,
                    new_email=model.email,
                    cryptocurrency_symbol=model.cryptocurrency,
                    threshold_price=model.threshold_price,
                    created_at=model.created_at,
                )
                events.append(event)

            if model.threshold_price:
                logger.info(
                    "Changing threshold price",
                    old_threshold=str(old_threshold_price),
                    new_threshold=str(model.threshold_price),
                )
                event = AlertUpdatedEvent.on_threshold_price_change(
                    alert_id=model.id,
                    email=model.email,
                    cryptocurrency_symbol=model.cryptocurrency,
                    old_threshold_price=old_threshold_price,
                    new_threshold_price=model.threshold_price,
                    created_at=model.created_at,
                )
                logger.info("Changed threshold price, resetting trigger")
                model = model.reset_trigger()
                events.append(event)

            updated_entity = await self._repository.update(model)

            logger.info(f"Created event(s) to publish", alert_id=str(alert_id), len_=len(events))
            for event in events:
                logger.info(
                    "Publishing alert update event",
                    event_id=str(event.event_id),
                    topic=broker_settings.alert_updated_topic,
                )
                await self._broker.publish(topic=broker_settings.alert_updated_topic, event=event)
                logger.info("Publication sent successfully", event_id=str(event.event_id))

            logger.info("Alert updated successfully")

            return updated_entity

        except AlertNotFound as e:
            logger.error(
                "Alert not found during update operation",
                alert_id=str(alert_id),
                error=str(e),
            )
            raise

        except RepositoryError as e:
            logger.error(
                "Repository error during alert update",
                alert_id=str(alert_id),
                error=str(e),
                exc_info=True,
            )
            raise

        except SQLAlchemyError as e:
            logger.error(
                "Database error during alert update",
                alert_id=str(alert_id),
                error=str(e),
                exc_info=True,
            )
            raise RepositoryError(f"Failed to update alert {alert_id}: database error") from e

        except DomainValidationError as e:
            logger.error(
                "Domain validation error during alert update",
                alert_id=str(alert_id),
                error=str(e),
                exc_info=True,
            )
            raise

        except Exception as e:
            logger.error(
                "Unexpected error during alert update",
                alert_id=str(alert_id),
                error=str(e),
                exc_info=True,
            )
            raise RepositoryError(f"Unexpected error while updating alert {alert_id}") from e
