from src.core.database import AsyncSessionLocal
from src.services.categories.application.usecase.get_categories_use_case import GetCategoriesUseCase
from src.services.categories.domain.dto.category_schemas import CategoryResponse
from src.services.categories.infrastructure.adapters.postgres import PostgresCategoryRepository


async def get_all() -> list[CategoryResponse]:
    repo = PostgresCategoryRepository(AsyncSessionLocal)
    use_case = GetCategoriesUseCase(repo)
    categories = await use_case.execute()
    return [CategoryResponse.from_entity(c) for c in categories]