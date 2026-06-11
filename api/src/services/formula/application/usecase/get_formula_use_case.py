from src.core.exceptions import FormulaNotFoundException
from src.services.formula.domain.entities.efficiency_formula import EfficiencyFormula
from src.services.formula.domain.repository import IFormulaRepository


class GetFormulaUseCase:

    def __init__(self, repository: IFormulaRepository):
        self._repo = repository

    async def get_active(self) -> EfficiencyFormula:
        formula = await self._repo.get_active()
        if not formula:
            raise FormulaNotFoundException()
        return formula

    async def get_all(self) -> list[EfficiencyFormula]:
        return await self._repo.get_all()

    async def get_by_id(self, formula_id: int) -> EfficiencyFormula:
        formula = await self._repo.get_by_id(formula_id)
        if not formula:
            raise FormulaNotFoundException()
        return formula