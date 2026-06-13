from src.core.database import AsyncSessionLocal
from src.services.product_specifications.application.usecase.delete_specification_use_case import (
    DeleteSpecificationUseCase,
)
from src.services.product_specifications.infrastructure.adapters.postgres import (
    PostgresSpecificationRepository,
)


async def delete(product_id: int, specification_id: int) -> dict:
    repo = PostgresSpecificationRepository(AsyncSessionLocal)
    use_case = DeleteSpecificationUseCase(repo)
    await use_case.execute(product_id, specification_id)
    return {"message": "Especificación eliminada exitosamente"}