from fastapi import APIRouter, Depends

from src.core.dependencies import get_current_user, require_admin_or_profesor
from src.services.formula.domain.dto.formula_schema import FormulaResponse
from src.services.formula.domain.dto.update_formula_schema import UpdateFormulaRequest
from src.services.formula.infrastructure.controllers.activate_formula_controller import activate
from src.services.formula.infrastructure.controllers.get_active_formula_controller import get_active
from src.services.formula.infrastructure.controllers.get_all_formulas_controller import get_all
from src.services.formula.infrastructure.controllers.get_formula_by_id_controller import get_by_id
from src.services.formula.infrastructure.controllers.update_formula_controller import update

router = APIRouter()


@router.get("/active", response_model=FormulaResponse, summary="Obtener fórmula activa")
async def get_active_formula(current_user: dict = Depends(get_current_user)):
    return await get_active()


@router.get("/", response_model=list[FormulaResponse], summary="Listar todas las fórmulas")
async def get_all_formulas(current_user: dict = Depends(get_current_user)):
    return await get_all()


@router.get("/{formula_id}", response_model=FormulaResponse, summary="Obtener fórmula por ID")
async def get_formula(formula_id: int, current_user: dict = Depends(get_current_user)):
    return await get_by_id(formula_id)


@router.put("/{formula_id}", response_model=FormulaResponse, summary="Editar fórmula")
async def update_formula(
    formula_id: int,
    body: UpdateFormulaRequest,
    current_user: dict = Depends(require_admin_or_profesor),
):
    return await update(formula_id, body, current_user["user_id"])


@router.patch(
    "/{formula_id}/activate",
    response_model=FormulaResponse,
    summary="Cambiar fórmula activa",
)
async def activate_formula(formula_id: int, current_user: dict = Depends(require_admin_or_profesor)):
    return await activate(formula_id, current_user["user_id"])
