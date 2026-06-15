from abc import ABC, abstractmethod

from src.services.product_specifications.domain.entities.specification import Specification


class ISpecificationRepository(ABC):

    @abstractmethod
    async def get_by_product(self, product_id: int) -> list[Specification]:
        ...

    @abstractmethod
    async def get_by_id(self, specification_id: int) -> Specification | None:
        ...

    @abstractmethod
    async def create(self, specification: Specification) -> Specification:
        ...

    @abstractmethod
    async def update(self, specification: Specification) -> Specification:
        ...

    @abstractmethod
    async def delete(self, specification_id: int) -> None:
        ...