from src.core.database import AsyncSessionLocal
from src.services.formula.application.usecase.update_formula_use_case import UpdateFormulaUseCase
from src.services.formula.domain.dto.formula_schema import FormulaResponse
from src.services.formula.infrastructure.adapters.MySQL import FormulaRepository


async def activate(formula_id: int, updated_by: int) -> FormulaResponse:
    repo = FormulaRepository(AsyncSessionLocal)
    formula = await UpdateFormulaUseCase(repo).set_active(
        formula_id=formula_id,
        updated_by=updated_by,
    )
    return FormulaResponse.from_entity(formula)
