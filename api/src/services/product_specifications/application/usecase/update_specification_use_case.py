from src.core.exceptions import ForbiddenException, SpecificationNotFoundException
from src.services.product_specifications.domain.entities.specification import Specification
from src.services.product_specifications.domain.repository import ISpecificationRepository


class UpdateSpecificationUseCase:
    def __init__(self, spec_repository: ISpecificationRepository):
        self._spec_repo = spec_repository

    async def execute(self, product_id: int, specification_id: int, **kwargs) -> Specification:
        spec = await self._spec_repo.get_by_id(specification_id)
        if not spec:
            raise SpecificationNotFoundException()

        if spec.product_id != product_id:
            raise ForbiddenException()

        for key, value in kwargs.items():
            if value is not None:
                setattr(spec, key, value)

        return await self._spec_repo.update(spec)