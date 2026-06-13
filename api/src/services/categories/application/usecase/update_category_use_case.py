from src.core.exceptions import CategoryAlreadyExistsException, CategoryNotFoundException
from src.services.categories.domain.entities.category import Category
from src.services.categories.domain.repository import ICategoryRepository


class UpdateCategoryUseCase:
    def __init__(self, repository: ICategoryRepository):
        self._repo = repository

    async def execute(self, category_id: int, **kwargs) -> Category:
        category = await self._repo.get_by_id(category_id)
        if not category:
            raise CategoryNotFoundException()

        if "name" in kwargs and kwargs["name"] != category.name:
            existing = await self._repo.get_by_name(kwargs["name"])
            if existing:
                raise CategoryAlreadyExistsException()

        for key, value in kwargs.items():
            if value is not None:
                setattr(category, key, value)

        return await self._repo.update(category)