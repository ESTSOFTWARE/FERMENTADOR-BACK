from src.core.exceptions import ProductNotFoundException
from src.services.product_benefits.domain.entities.benefit import Benefit
from src.services.product_benefits.domain.repository import IBenefitRepository
from src.services.products.domain.repository import IProductRepository


class CreateBenefitUseCase:
    def __init__(self, benefit_repository: IBenefitRepository, product_repository: IProductRepository):
        self._benefit_repo  = benefit_repository
        self._product_repo  = product_repository

    async def execute(self, product_id: int, title: str, description: str | None) -> Benefit:
        product = await self._product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException()

        return await self._benefit_repo.create(Benefit(
            id=None,
            product_id=product_id,
            title=title,
            description=description
        ))