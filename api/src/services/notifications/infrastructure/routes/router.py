from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from src.core.dependencies import get_current_user
from src.services.notifications.domain.dto.ml_result_dto import MlResultDTO
from src.services.notifications.domain.dto.notification_schema import NotificationResponse
from src.services.notifications.infrastructure.controllers.get_notifications_controller import (
    get_all,
)
from src.services.notifications.infrastructure.controllers.mark_all_as_read_controller import (
    mark_all_as_read,
)
from src.services.notifications.infrastructure.controllers.mark_one_as_read_controller import (
    mark_one_as_read,
)
from src.services.notifications.infrastructure.controllers.receive_ml_result_controller import (
    receive_ml_result,
)

router = APIRouter()


@router.get(
    "/",
    response_model=list[NotificationResponse],
    summary="Listar notificaciones del usuario autenticado",
)
async def get_notifications(
    only_unread: bool = Query(default=False),
    current_user: dict = Depends(get_current_user),
):
    return await get_all(user_id=current_user["user_id"], only_unread=only_unread)


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse | None,
    summary="Marcar notificación como leída",
)
async def mark_as_read(notification_id: int, current_user: dict = Depends(get_current_user)):
    return await mark_one_as_read(notification_id)


@router.patch("/read-all", status_code=204, summary="Marcar todas las notificaciones como leídas")
async def mark_all_read(current_user: dict = Depends(get_current_user)):
    await mark_all_as_read(current_user["user_id"])


class DeviceTokenRequest(BaseModel):
    token:    str
    platform: str = "android"


@router.post("/device-token", status_code=204, summary="Registrar token FCM del dispositivo (push)")
async def register_device_token(
    body: DeviceTokenRequest,
    current_user: dict = Depends(get_current_user),
):
    from src.core.fcm.fcm_service import save_device_token
    await save_device_token(current_user["user_id"], body.token, body.platform)

@router.post(
    "/ml-results",
    status_code=204,
    summary="Recibe resultados del microservicio de ML (anomalías y predicciones de eficiencia)",
)
async def ml_results(body: MlResultDTO):
    await receive_ml_result(body.model_dump(mode="json"))