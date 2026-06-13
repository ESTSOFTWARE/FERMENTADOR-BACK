from src.core.exceptions import CategoryNotFoundException
from src.services.categories.domain.entities.category import Category
from src.services.categories.domain.repository import ICategoryRepository


class GetCategoryByIdUseCase:
    def __init__(self, repository: ICategoryRepository):
        self._repo = repository

    async def execute(self, category_id: int) -> Category:
        category = await self._repo.get_by_id(category_id)
        if not category:
            raise CategoryNotFoundException()
        return category