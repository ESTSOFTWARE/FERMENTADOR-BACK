from abc import ABC, abstractmethod

from src.services.product_includes.domain.entities.include import Include


class IIncludeRepository(ABC):

    @abstractmethod
    async def get_by_product(self, product_id: int) -> list[Include]:
        ...

    @abstractmethod
    async def get_by_id(self, include_id: int) -> Include | None:
        ...

    @abstractmethod
    async def create(self, include: Include) -> Include:
        ...

    @abstractmethod
    async def update(self, include: Include) -> Include:
        ...

    @abstractmethod
    async def delete(self, include_id: int) -> None:
        ...