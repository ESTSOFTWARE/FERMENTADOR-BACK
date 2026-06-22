from fastapi import APIRouter, Depends

from src.core.dependencies import require_admin_or_soporte
from src.services.fermentadores.domain.dto.fermentador_schema import (
    FermentadorResponse,
    UpdateFermentadorRequest,
)
from src.services.fermentadores.infrastructure.controllers.create_fermentador_controller import (
    create_fermentador,
)
from src.services.fermentadores.infrastructure.controllers.get_fermentadores_controller import (
    get_fermentadores,
)
from src.services.fermentadores.infrastructure.controllers.update_fermentador_controller import (
    update_fermentador,
)

router = APIRouter()


@router.get("/", response_model=list[FermentadorResponse], summary="Listar fermentadores (admin o soporte)")
async def list_fermentadores_route(_: dict = Depends(require_admin_or_soporte)):
    return await get_fermentadores()


@router.post("/", response_model=FermentadorResponse, status_code=201, summary="Registrar fermentador (admin o soporte)")
async def create_fermentador_route(current_user: dict = Depends(require_admin_or_soporte)):
    return await create_fermentador(created_by=current_user["user_id"])


@router.patch("/{fermentador_id}", response_model=FermentadorResponse, summary="Actualizar fermentador (admin o soporte)")
async def update_fermentador_route(
    fermentador_id: int,
    body: UpdateFermentadorRequest,
    _: dict = Depends(require_admin_or_soporte),
):
    return await update_fermentador(fermentador_id, body)
