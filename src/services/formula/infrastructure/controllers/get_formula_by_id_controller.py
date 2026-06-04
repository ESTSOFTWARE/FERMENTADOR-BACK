from src.core.database import AsyncSessionLocal
from src.services.formula.application.usecase.get_formula_use_case import GetFormulaUseCase
from src.services.formula.domain.dto.formula_schema import FormulaResponse
from src.services.formula.infrastructure.adapters.postgres import FormulaRepository


async def get_by_id(formula_id: int) -> FormulaResponse:
    repo = FormulaRepository(AsyncSessionLocal)
    formula = await GetFormulaUseCase(repo).get_by_id(formula_id)
    return FormulaResponse.from_entity(formula)
