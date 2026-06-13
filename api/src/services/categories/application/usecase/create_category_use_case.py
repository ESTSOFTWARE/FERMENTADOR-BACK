from src.core.exceptions import CategoryAlreadyExistsException
from src.services.categories.domain.entities.category import Category
from src.services.categories.domain.repository import ICategoryRepository


class CreateCategoryUseCase:
    def __init__(self, repository: ICategoryRepository):
        self._repo = repository

    async def execute(self, name: str, description: str | None) -> Category:
        existing = await self._repo.get_by_name(name)
        if existing:
            raise CategoryAlreadyExistsException()

        return await self._repo.create(Category(
            id=None,
            name=name,
            description=description
        ))