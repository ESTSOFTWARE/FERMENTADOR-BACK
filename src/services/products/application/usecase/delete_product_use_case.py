from src.core.exceptions import ProductNotFoundException
from src.services.products.domain.repository import IProductRepository


class DeleteProductUseCase:
    def __init__(self, product_repository: IProductRepository):
        self._product_repo = product_repository

    async def execute(self, product_id: int) -> None:
        product = await self._product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException()
        await self._product_repo.delete(product_id)
