from src.core.database import AsyncSessionLocal
from src.services.categories.application.usecase.delete_category_use_case import (
    DeleteCategoryUseCase,
)
from src.services.categories.infrastructure.adapters.postgres import PostgresCategoryRepository


async def delete(category_id: int) -> dict:
    repo = PostgresCategoryRepository(AsyncSessionLocal)
    use_case = DeleteCategoryUseCase(repo)
    await use_case.execute(category_id)
    return {"message": "Categoría eliminada exitosamente"}