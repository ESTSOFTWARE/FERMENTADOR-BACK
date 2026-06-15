from src.core.exceptions import ProductNotFoundException
from src.services.products.domain.entities.product import Product
from src.services.products.domain.repository import IProductRepository


class GetRelatedProductsUseCase:
    def __init__(self, product_repository: IProductRepository):
        self._product_repo = product_repository

    async def execute(self, product_id: int, limit: int = 6) -> list[Product]:
        product = await self._product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException()

        if not product.category_id:
            return []

        return await self._product_repo.get_related(
            product_id=product_id,
            category_id=product.category_id,
            limit=limit
        )