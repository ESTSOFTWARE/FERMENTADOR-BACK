from src.core.exceptions import ProductNotFoundException
from src.services.products.domain.entities.product import Product
from src.services.products.domain.repository import IProductRepository

class GetProductByIdUseCase:
    def __init__(self, product_repository: IProductRepository):
        self._product_repo = product_repository

    async def execute(self, product_id: int) -> Product:
        product = await self._product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException()
        return product
