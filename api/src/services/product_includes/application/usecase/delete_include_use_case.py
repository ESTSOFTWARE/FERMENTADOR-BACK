from src.core.exceptions import ForbiddenException, IncludeNotFoundException
from src.services.product_includes.domain.repository import IIncludeRepository


class DeleteIncludeUseCase:
    def __init__(self, include_repository: IIncludeRepository):
        self._include_repo = include_repository

    async def execute(self, product_id: int, include_id: int) -> None:
        include = await self._include_repo.get_by_id(include_id)
        if not include:
            raise IncludeNotFoundException()

        if include.product_id != product_id:
            raise ForbiddenException()

        await self._include_repo.delete(include_id)