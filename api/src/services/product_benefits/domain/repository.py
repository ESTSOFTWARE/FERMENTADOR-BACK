from abc import ABC, abstractmethod

from src.services.product_benefits.domain.entities.benefit import Benefit


class IBenefitRepository(ABC):

    @abstractmethod
    async def get_by_product(self, product_id: int) -> list[Benefit]:
        ...

    @abstractmethod
    async def get_by_id(self, benefit_id: int) -> Benefit | None:
        ...

    @abstractmethod
    async def create(self, benefit: Benefit) -> Benefit:
        ...

    @abstractmethod
    async def update(self, benefit: Benefit) -> Benefit:
        ...

    @abstractmethod
    async def delete(self, benefit_id: int) -> None:
        ...