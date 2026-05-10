from src.core.database import AsyncSessionLocal
from src.services.formula.application.usecase.get_formula_use_case import GetFormulaUseCase
from src.services.formula.domain.dto.formula_schema import FormulaResponse
from src.services.formula.infrastructure.adapters.MySQL import FormulaRepository


async def get_all() -> list[FormulaResponse]:
    repo = FormulaRepository(AsyncSessionLocal)
    formulas = await GetFormulaUseCase(repo).get_all()
    return [FormulaResponse.from_entity(f) for f in formulas]
