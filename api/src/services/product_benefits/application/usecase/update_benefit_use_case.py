from src.core.exceptions import BenefitNotFoundException, ForbiddenException
from src.services.product_benefits.domain.entities.benefit import Benefit
from src.services.product_benefits.domain.repository import IBenefitRepository


class UpdateBenefitUseCase:
    def __init__(self, benefit_repository: IBenefitRepository):
        self._benefit_repo = benefit_repository

    async def execute(self, product_id: int, benefit_id: int, **kwargs) -> Benefit:
        benefit = await self._benefit_repo.get_by_id(benefit_id)
        if not benefit:
            raise BenefitNotFoundException()

        if benefit.product_id != product_id:
            raise ForbiddenException()

        for key, value in kwargs.items():
            if value is not None:
                setattr(benefit, key, value)

        return await self._benefit_repo.update(benefit) 