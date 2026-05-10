from fastapi import APIRouter, Depends, Query

from src.core.dependencies import get_current_user
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
