import uuid

from dishka.integrations.fastapi import inject, FromDishka
from fastapi import APIRouter

from application.use_cases.delete_alert import DeleteAlertUseCase
from application.use_cases.get_alerts_list_by_email import GetAlertsUseCase
from application.use_cases.save_alert_to_database import SaveAlertToDBUseCase
from application.use_cases.update_alert import UpdateAlertUseCase
from presentation.api.v1.mappers.to_response import AlertPresentationMapper
from presentation.api.v1.schemas.alert import AlertResponse, AlertCreateRequest, AlertUpdateRequest

router = APIRouter(prefix="/alerts")

@router.get("/v1/{email}", response_model=list[AlertResponse], status_code=200)
@inject
async def get_alerts_by_email(
        email: str,
        use_case: FromDishka[GetAlertsUseCase],
        mapper: FromDishka[AlertPresentationMapper]
) -> list[AlertResponse]:
    """Get alerts by email."""
    entities = await use_case.execute(email=email)
    return [mapper.from_entity_to_pydantic(entity) for entity in entities]

@router.post("/v1/", status_code=201)
@inject
async def create_alert(
    alert_data: AlertCreateRequest,
    use_case: FromDishka[SaveAlertToDBUseCase],
) -> dict:
    """Create new alert."""
    await use_case.execute(alert_data)
    return {"message": "Alert created successfully"}

@router.delete("/v1/delete/{alert_id}")
@inject
async def delete_alert(
        alert_id: uuid.UUID,
        email: str,
        use_case: FromDishka[DeleteAlertUseCase]
)-> dict:
    """Delete alert belonging to the provided email."""
    await use_case.execute(
        alert_id=alert_id,
        email=email
    )
    return {"message": "alert deleted successfully"}

@router.put("/v1/update/{alert_id}", response_model=AlertResponse)
@inject
async def update_alert(
        alert_id: uuid.UUID,
        alert_to_update: AlertUpdateRequest,
        use_case: FromDishka[UpdateAlertUseCase],
        mapper: FromDishka[AlertPresentationMapper],
) -> AlertResponse:
    """Update existing alert with partial data.
    
    Allows updating email, threshold_price, and is_active fields.
    Cryptocurrency cannot be changed - delete and recreate alert instead.
    
    Returns updated alert data with all fields.
    """
    entity = await use_case.execute(
        alert_to_update=alert_to_update,
        alert_id=alert_id,
    )
    return mapper.from_entity_to_pydantic(entity)

