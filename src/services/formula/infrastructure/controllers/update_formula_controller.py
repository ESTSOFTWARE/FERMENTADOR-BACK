from src.core.database import AsyncSessionLocal
from src.services.formula.application.usecase.update_formula_use_case import UpdateFormulaUseCase
from src.services.formula.domain.dto.formula_schema import FormulaResponse
from src.services.formula.domain.dto.update_formula_schema import UpdateFormulaRequest
from src.services.formula.infrastructure.adapters.postgres import FormulaRepository


async def update(formula_id: int, body: UpdateFormulaRequest, updated_by: int) -> FormulaResponse:
    repo = FormulaRepository(AsyncSessionLocal)
    formula = await UpdateFormulaUseCase(repo).execute(
        formula_id=formula_id,
        updated_by=updated_by,
        name=body.name,
        conversion_factor=body.conversion_factor,
        description=body.description,
    )
    return FormulaResponse.from_entity(formula)
