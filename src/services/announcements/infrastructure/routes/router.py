from fastapi import APIRouter, Depends

from src.core.dependencies import require_any_role, require_soporte
from src.services.announcements.domain.dto.announcement_schema import (
    AnnouncementResponse,
    CreateAnnouncementRequest,
    PinAnnouncementRequest,
    UpdateAnnouncementRequest,
)
from src.services.announcements.infrastructure.controllers.create_announcement_controller import (
    create_announcement,
)
from src.services.announcements.infrastructure.controllers.delete_announcement_controller import (
    delete_announcement,
)
from src.services.announcements.infrastructure.controllers.get_announcement_by_id_controller import (
    get_announcement_by_id,
)
from src.services.announcements.infrastructure.controllers.get_announcements_controller import (
    get_announcements,
)
from src.services.announcements.infrastructure.controllers.pin_announcement_controller import (
    pin_announcement,
)
from src.services.announcements.infrastructure.controllers.unpin_announcement_controller import (
    unpin_announcement,
)
from src.services.announcements.infrastructure.controllers.update_announcement_controller import (
    update_announcement,
)

router = APIRouter()


@router.get(
    "/",
    response_model=list[AnnouncementResponse],
    summary="Obtener todos los anuncios",
)
async def get_announcements_route(_: dict = Depends(require_any_role)):
    return await get_announcements()


@router.get(
    "/{announcement_id}",
    response_model=AnnouncementResponse,
    summary="Obtener anuncio por ID",
)
async def get_announcement_by_id_route(
    announcement_id: int,
    _: dict = Depends(require_any_role),
):
    return await get_announcement_by_id(announcement_id)


@router.post(
    "/",
    response_model=AnnouncementResponse,
    status_code=201,
    summary="Crear anuncio (solo admin)",
)
async def create_announcement_route(
    body: CreateAnnouncementRequest,
    current_user: dict = Depends(require_soporte),
):
    return await create_announcement(body, creator_id=current_user["user_id"])


@router.put(
    "/{announcement_id}",
    response_model=AnnouncementResponse,
    summary="Actualizar anuncio (solo admin)",
)
async def update_announcement_route(
    announcement_id: int,
    body: UpdateAnnouncementRequest,
    _: dict = Depends(require_soporte),
):
    return await update_announcement(announcement_id, body)


@router.delete(
    "/{announcement_id}",
    status_code=204,
    summary="Eliminar anuncio (solo admin)",
)
async def delete_announcement_route(
    announcement_id: int,
    _: dict = Depends(require_soporte),
):
    await delete_announcement(announcement_id)


@router.post(
    "/{announcement_id}/pin",
    response_model=AnnouncementResponse,
    summary="Fijar anuncio (solo soporte)",
)
async def pin_announcement_route(
    announcement_id: int,
    body: PinAnnouncementRequest,
    _: dict = Depends(require_soporte),
):
    return await pin_announcement(announcement_id, body.duration_days)


@router.delete(
    "/{announcement_id}/pin",
    response_model=AnnouncementResponse,
    summary="Desfijar anuncio (solo soporte)",
)
async def unpin_announcement_route(
    announcement_id: int,
    _: dict = Depends(require_soporte),
):
    return await unpin_announcement(announcement_id)
