from fastapi import APIRouter, Depends

from src.core.dependencies import require_admin
from src.services.product_includes.domain.dto.include_schema import (
    CreateIncludeRequest,
    IncludeResponse,
    UpdateIncludeRequest,
)
from src.services.product_includes.infrastructure.controllers.create_include_controller import (
    create,
)
from src.services.product_includes.infrastructure.controllers.delete_include_controller import (
    delete,
)
from src.services.product_includes.infrastructure.controllers.get_includes_controller import get_all
from src.services.product_includes.infrastructure.controllers.update_include_controller import (
    update,
)

router = APIRouter()


@router.get("/", response_model=list[IncludeResponse], summary="Obtener elementos incluidos del producto")
async def get_includes(product_id: int):
    return await get_all(product_id)


@router.post("/", response_model=IncludeResponse, status_code=201, summary="Crear elemento incluido (solo admin)")
async def create_include(product_id: int, body: CreateIncludeRequest, current_user: dict = Depends(require_admin)):
    return await create(product_id, body)


@router.put("/{include_id}", response_model=IncludeResponse, summary="Actualizar elemento incluido (solo admin)")
async def update_include(product_id: int, include_id: int, body: UpdateIncludeRequest, current_user: dict = Depends(require_admin)):
    return await update(product_id, include_id, body)


@router.delete("/{include_id}", status_code=200, summary="Eliminar elemento incluido (solo admin)")
async def delete_include(product_id: int, include_id: int, current_user: dict = Depends(require_admin)):
    return await delete(product_id, include_id)