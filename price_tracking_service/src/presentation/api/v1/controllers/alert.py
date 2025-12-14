import uuid

from dishka.integrations.fastapi import inject, FromDishka
from fastapi import APIRouter

from application.use_cases.get_alerts_list_by_email import GetAlertsUseCase
from domain.entities.alert import AlertEntity
from presentation.api.v1.schemas.alert import AlertResponse

router = APIRouter(prefix="/alerts")

@router.get("/v1/", response_model=list[AlertResponse], status_code=200)
@inject
async def get_alerts_by_email(
        email: str,
        use_case: FromDishka[GetAlertsUseCase]
) -> list[AlertEntity]:
    """Get alerts by email."""
    return await use_case.execute(email=email)

