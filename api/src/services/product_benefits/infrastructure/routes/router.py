from fastapi import APIRouter, Depends

from src.core.dependencies import require_admin
from src.services.product_benefits.domain.dto.benefit_schema import (
    BenefitResponse,
    CreateBenefitRequest,
    UpdateBenefitRequest,
)
from src.services.product_benefits.infrastructure.controllers.create_benefit_controller import (
    create,
)
from src.services.product_benefits.infrastructure.controllers.delete_benefit_controller import (
    delete,
)
from src.services.product_benefits.infrastructure.controllers.get_benefits_controller import get_all
from src.services.product_benefits.infrastructure.controllers.update_benefit_controller import (
    update,
)

router = APIRouter()


@router.get("/", response_model=list[BenefitResponse], summary="Obtener beneficios del producto")
async def get_benefits(product_id: int):
    return await get_all(product_id)


@router.post("/", response_model=BenefitResponse, status_code=201, summary="Crear beneficio (solo admin)")
async def create_benefit(product_id: int, body: CreateBenefitRequest, current_user: dict = Depends(require_admin)):
    return await create(product_id, body)


@router.put("/{benefit_id}", response_model=BenefitResponse, summary="Actualizar beneficio (solo admin)")
async def update_benefit(product_id: int, benefit_id: int, body: UpdateBenefitRequest, current_user: dict = Depends(require_admin)):
    return await update(product_id, benefit_id, body)


@router.delete("/{benefit_id}", status_code=200, summary="Eliminar beneficio (solo admin)")
async def delete_benefit(product_id: int, benefit_id: int, current_user: dict = Depends(require_admin)):
    return await delete(product_id, benefit_id)