from src.services.categories.domain.entities.category import Category
from src.services.categories.domain.repository import ICategoryRepository


class GetCategoriesUseCase:
    def __init__(self, repository: ICategoryRepository):
        self._repo = repository

    async def execute(self) -> list[Category]:
        return await self._repo.get_all()