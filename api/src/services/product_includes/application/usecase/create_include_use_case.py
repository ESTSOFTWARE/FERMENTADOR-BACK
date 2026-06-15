from src.core.exceptions import ProductNotFoundException
from src.services.product_includes.domain.entities.include import Include
from src.services.product_includes.domain.repository import IIncludeRepository
from src.services.products.domain.repository import IProductRepository


class CreateIncludeUseCase:
    def __init__(self, include_repository: IIncludeRepository, product_repository: IProductRepository):
        self._include_repo = include_repository
        self._product_repo = product_repository

    async def execute(self, product_id: int, description: str) -> Include:
        product = await self._product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException()

        return await self._include_repo.create(Include(
            id=None,
            product_id=product_id,
            description=description
        ))