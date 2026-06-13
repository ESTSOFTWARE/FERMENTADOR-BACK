from src.core.database import AsyncSessionLocal
from src.services.product_benefits.application.usecase.get_benefits_use_case import (
    GetBenefitsUseCase,
)
from src.services.product_benefits.domain.dto.benefit_schema import BenefitResponse
from src.services.product_benefits.infrastructure.adapters.postgres import PostgresBenefitRepository
from src.services.products.infrastructure.adapters.postgres import PostgresProductRepository


async def get_all(product_id: int) -> list[BenefitResponse]:
    benefit_repo = PostgresBenefitRepository(AsyncSessionLocal)
    product_repo = PostgresProductRepository(AsyncSessionLocal)
    use_case = GetBenefitsUseCase(benefit_repo, product_repo)
    benefits = await use_case.execute(product_id)
    return [BenefitResponse.from_entity(b) for b in benefits]