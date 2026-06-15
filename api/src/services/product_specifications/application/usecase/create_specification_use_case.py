from src.core.exceptions import ProductNotFoundException
from src.services.product_specifications.domain.entities.specification import Specification
from src.services.product_specifications.domain.repository import ISpecificationRepository
from src.services.products.domain.repository import IProductRepository


class CreateSpecificationUseCase:
    def __init__(self, spec_repository: ISpecificationRepository, product_repository: IProductRepository):
        self._spec_repo    = spec_repository
        self._product_repo = product_repository

    async def execute(self, product_id: int, name: str, value: str) -> Specification:
        product = await self._product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException()

        return await self._spec_repo.create(Specification(
            id=None,
            product_id=product_id,
            name=name,
            value=value
        ))