from abc import ABC, abstractmethod

from src.services.categories.domain.entities.category import Category


class ICategoryRepository(ABC):

    @abstractmethod
    async def get_all(self) -> list[Category]:
        ...

    @abstractmethod
    async def get_by_id(self, category_id: int) -> Category | None:
        ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Category | None:
        ...

    @abstractmethod
    async def create(self, category: Category) -> Category:
        ...

    @abstractmethod
    async def update(self, category: Category) -> Category:
        ...

    @abstractmethod
    async def delete(self, category_id: int) -> None:
        ...