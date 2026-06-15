from src.core.database import AsyncSessionLocal
from src.services.categories.application.usecase.create_category_use_case import (
    CreateCategoryUseCase,
)
from src.services.categories.domain.dto.category_schemas import (
    CategoryResponse,
    CreateCategoryRequest,
)
from src.services.categories.infrastructure.adapters.postgres import PostgresCategoryRepository


async def create(body: CreateCategoryRequest) -> CategoryResponse:
    repo = PostgresCategoryRepository(AsyncSessionLocal)
    use_case = CreateCategoryUseCase(repo)
    category = await use_case.execute(name=body.name, description=body.description)
    return CategoryResponse.from_entity(category)