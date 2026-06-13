from src.core.exceptions import CategoryNotFoundException
from src.services.categories.domain.repository import ICategoryRepository


class DeleteCategoryUseCase:
    def __init__(self, repository: ICategoryRepository):
        self._repo = repository

    async def execute(self, category_id: int) -> None:
        category = await self._repo.get_by_id(category_id)
        if not category:
            raise CategoryNotFoundException()
        await self._repo.delete(category_id)