from abc import ABC, abstractmethod
from src.services.formula.domain.entities.efficiency_formula import EfficiencyFormula


class IFormulaRepository(ABC):

    @abstractmethod
    async def get_active(self) -> EfficiencyFormula | None:
        ...

    @abstractmethod
    async def get_by_id(self, formula_id: int) -> EfficiencyFormula | None:
        ...

    @abstractmethod
    async def get_all(self) -> list[EfficiencyFormula]:
        ...

    @abstractmethod
    async def update(
        self,
        formula_id:        int,
        name:              str | None,
        conversion_factor: float | None,
        description:       str | None,
        updated_by:        int,
    ) -> EfficiencyFormula:
        ...

    @abstractmethod
    async def set_active(self, formula_id: int) -> EfficiencyFormula:
        ...