from abc import ABC, abstractmethod

from src.services.products.domain.entities.product import Product


class IProductRepository(ABC):

    @abstractmethod
    async def get_all(self, page: int = 1, limit: int = 10, search: str | None = None) -> list[Product]:
        ...

    @abstractmethod
    async def get_by_id(self, product_id: int) -> Product | None:
        ...

    @abstractmethod
    async def get_by_sku(self, sku: str) -> Product | None:
        ...

    @abstractmethod
    async def get_related(self, product_id: int, category_id: int, limit: int = 6) -> list[Product]:
        ...

    @abstractmethod
    async def update_rating(self, product_id: int, rating: float) -> None:
        ...

    @abstractmethod
    async def create(self, product: Product) -> Product:
        ...

    @abstractmethod
    async def update(self, product: Product) -> Product:
        ...

    @abstractmethod
    async def delete(self, product_id: int) -> None:
        ...

    @abstractmethod
    async def count(self, search: str | None = None) -> int:
        ...