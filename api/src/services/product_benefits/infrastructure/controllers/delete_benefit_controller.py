from src.core.database import AsyncSessionLocal
from src.services.product_benefits.application.usecase.delete_benefit_use_case import (
    DeleteBenefitUseCase,
)
from src.services.product_benefits.infrastructure.adapters.postgres import PostgresBenefitRepository


async def delete(product_id: int, benefit_id: int) -> dict:
    repo = PostgresBenefitRepository(AsyncSessionLocal)
    use_case = DeleteBenefitUseCase(repo)
    await use_case.execute(product_id, benefit_id)
    return {"message": "Beneficio eliminado exitosamente"}