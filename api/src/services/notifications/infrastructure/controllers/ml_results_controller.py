from fastapi import APIRouter

from src.services.notifications.application.usecase.send_ml_result_use_case import (
    SendMlResultUseCase,
)
from src.services.notifications.domain.dto.ml_result_dto import MlResultDTO

router = APIRouter()


@router.post("/ml-results", status_code=204, summary="Recibe resultados del microservicio de ML")
async def receive_ml_result(body: MlResultDTO):
    await SendMlResultUseCase().execute(body.model_dump(mode="json"))