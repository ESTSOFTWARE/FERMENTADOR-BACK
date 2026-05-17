from fastapi import APIRouter, Depends

from src.core.dependencies import require_admin, require_any_role
from src.services.announcements.domain.dto.announcement_schema import (
    AnnouncementResponse,
    CreateAnnouncementRequest,
)
from src.services.announcements.infrastructure.controllers.create_announcement_controller import (
    create_announcement,
)
from src.services.announcements.infrastructure.controllers.delete_announcement_controller import (
    delete_announcement,
)
from src.services.announcements.infrastructure.controllers.get_announcements_controller import (
    get_announcements,
)

router = APIRouter()


@router.get(
    "/",
    response_model=list[AnnouncementResponse],
    summary="Obtener todos los anuncios",
)
async def get_announcements_route(_: dict = Depends(require_any_role)):
    return await get_announcements()


@router.post(
    "/",
    response_model=AnnouncementResponse,
    status_code=201,
    summary="Crear anuncio (solo admin)",
)
async def create_announcement_route(
    body: CreateAnnouncementRequest,
    _: dict = Depends(require_admin),
):
    return await create_announcement(body)


@router.delete(
    "/{announcement_id}",
    status_code=204,
    summary="Eliminar anuncio (solo admin)",
)
async def delete_announcement_route(
    announcement_id: int,
    _: dict = Depends(require_admin),
):
    await delete_announcement(announcement_id)
