from fastapi import APIRouter, Depends

from src.core.dependencies import require_soporte
from src.services.support.domain.dto.admin_schema import AdminResponse
from src.services.support.infrastructure.controllers.get_admin_by_id_controller import (
    get_admin_by_id_controller,
)
from src.services.support.infrastructure.controllers.get_admins_controller import (
    get_admins_controller,
)

router = APIRouter()


@router.get(
    "/admins",
    response_model=list[AdminResponse],
    summary="Obtener lista de administradores",
    description="Retorna todos los usuarios con rol de administrador (role_id = 1). Solo accesible para soporte.",
)
async def get_admins(
    current_user: dict = Depends(require_soporte),
    response: list[AdminResponse] = Depends(get_admins_controller),
):
    return response


@router.get(
    "/admins/{admin_id}",
    response_model=AdminResponse,
    summary="Obtener administrador por ID",
    description="Retorna la información detallada de un administrador específico (role_id = 1). Solo accesible para soporte.",
)
async def get_admin_by_id(
    admin_id: int,
    current_user: dict = Depends(require_soporte),
    response: AdminResponse = Depends(get_admin_by_id_controller),
):
    return response
