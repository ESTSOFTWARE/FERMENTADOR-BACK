from fastapi import APIRouter, Depends

from src.core.dependencies import require_admin_or_soporte
from src.services.product_specifications.domain.dto.specification_schema import (
    CreateSpecificationRequest,
    SpecificationResponse,
    UpdateSpecificationRequest,
)
from src.services.product_specifications.infrastructure.controllers.create_specification_controller import (
    create,
)
from src.services.product_specifications.infrastructure.controllers.delete_specification_controller import (
    delete,
)
from src.services.product_specifications.infrastructure.controllers.get_specifications_controller import (
    get_all,
)
from src.services.product_specifications.infrastructure.controllers.update_specification_controller import (
    update,
)

router = APIRouter()


@router.get("/", response_model=list[SpecificationResponse], summary="Obtener especificaciones del producto")
async def get_specifications(product_id: int):
    return await get_all(product_id)


@router.post("/", response_model=SpecificationResponse, status_code=201, summary="Crear especificación (solo admin)")
async def create_specification(product_id: int, body: CreateSpecificationRequest, current_user: dict = Depends(require_admin_or_soporte)):
    return await create(product_id, body)


@router.put("/{specification_id}", response_model=SpecificationResponse, summary="Actualizar especificación (solo admin)")
async def update_specification(product_id: int, specification_id: int, body: UpdateSpecificationRequest, current_user: dict = Depends(require_admin_or_soporte)):
    return await update(product_id, specification_id, body)


@router.delete("/{specification_id}", status_code=200, summary="Eliminar especificación (solo admin)")
async def delete_specification(product_id: int, specification_id: int, current_user: dict = Depends(require_admin_or_soporte)):
    return await delete(product_id, specification_id)