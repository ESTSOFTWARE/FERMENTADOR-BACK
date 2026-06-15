from src.core.database import AsyncSessionLocal
from src.services.categories.application.usecase.get_category_by_id_use_case import (
    GetCategoryByIdUseCase,
)
from src.services.categories.domain.dto.category_schemas import CategoryResponse
from src.services.categories.infrastructure.adapters.postgres import PostgresCategoryRepository


async def get_by_id(category_id: int) -> CategoryResponse:
    repo = PostgresCategoryRepository(AsyncSessionLocal)
    use_case = GetCategoryByIdUseCase(repo)
    category = await use_case.execute(category_id)
    return CategoryResponse.from_entity(category)