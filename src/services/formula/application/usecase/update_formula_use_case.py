from src.core.exceptions import BadRequestException, FormulaNotFoundException
from src.services.formula.domain.entities.efficiency_formula import EfficiencyFormula
from src.services.formula.domain.repository import IFormulaRepository


class UpdateFormulaUseCase:

    def __init__(self, repository: IFormulaRepository):
        self._repo = repository

    async def execute(
        self,
        formula_id:        int,
        updated_by:        int,
        name:              str | None = None,
        conversion_factor: float | None = None,
        description:       str | None = None,
    ) -> EfficiencyFormula:
        formula = await self._repo.get_by_id(formula_id)
        if not formula:
            raise FormulaNotFoundException()

        if conversion_factor is not None and conversion_factor <= 0:
            raise BadRequestException(
                "El factor de conversión debe ser mayor a 0"
            )

        return await self._repo.update(
            formula_id=formula_id,
            name=name,
            conversion_factor=conversion_factor,
            description=description,
            updated_by=updated_by,
        )

    async def set_active(
        self,
        formula_id: int,
        updated_by: int,
    ) -> EfficiencyFormula:
        formula = await self._repo.get_by_id(formula_id)
        if not formula:
            raise FormulaNotFoundException()

        return await self._repo.set_active(formula_id)