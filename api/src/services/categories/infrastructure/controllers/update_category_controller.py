from src.core.database import AsyncSessionLocal
from src.services.categories.application.usecase.update_category_use_case import (
    UpdateCategoryUseCase,
)
from src.services.categories.domain.dto.category_schemas import (
    CategoryResponse,
    UpdateCategoryRequest,
)
from src.services.categories.infrastructure.adapters.postgres import PostgresCategoryRepository


async def update(category_id: int, body: UpdateCategoryRequest) -> CategoryResponse:
    repo = PostgresCategoryRepository(AsyncSessionLocal)
    use_case = UpdateCategoryUseCase(repo)
    category = await use_case.execute(category_id, **body.model_dump(exclude_unset=True))
    return CategoryResponse.from_entity(category)