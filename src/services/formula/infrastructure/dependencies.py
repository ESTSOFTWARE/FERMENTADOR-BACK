from src.core.database import AsyncSessionLocal
from src.services.formula.infrastructure.adapters.postgres import FormulaRepository


def get_formula_repository() -> FormulaRepository:
    return FormulaRepository(AsyncSessionLocal)