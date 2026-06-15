from src.core.exceptions import ForbiddenException, SpecificationNotFoundException
from src.services.product_specifications.domain.repository import ISpecificationRepository


class DeleteSpecificationUseCase:
    def __init__(self, spec_repository: ISpecificationRepository):
        self._spec_repo = spec_repository

    async def execute(self, product_id: int, specification_id: int) -> None:
        spec = await self._spec_repo.get_by_id(specification_id)
        if not spec:
            raise SpecificationNotFoundException()

        if spec.product_id != product_id:
            raise ForbiddenException()

        await self._spec_repo.delete(specification_id)