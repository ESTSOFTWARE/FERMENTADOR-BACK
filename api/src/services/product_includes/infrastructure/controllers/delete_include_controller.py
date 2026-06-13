from src.core.database import AsyncSessionLocal
from src.services.product_includes.application.usecase.delete_include_use_case import (
    DeleteIncludeUseCase,
)
from src.services.product_includes.infrastructure.adapters.postgres import PostgresIncludeRepository


async def delete(product_id: int, include_id: int) -> dict:
    repo = PostgresIncludeRepository(AsyncSessionLocal)
    use_case = DeleteIncludeUseCase(repo)
    await use_case.execute(product_id, include_id)
    return {"message": "Elemento eliminado exitosamente"}