from src.services.products.domain.entities.product import Product
from src.services.products.domain.repository import IProductRepository

class GetProductsUseCase:
    def __init__(self, product_repository: IProductRepository):
        self._product_repo = product_repository

    async def execute(self, page: int = 1, limit: int = 10, search: str | None = None) -> tuple[list[Product], int]:
        products = await self._product_repo.get_all(page, limit, search)
        total = await self._product_repo.count(search)
        return products, total
