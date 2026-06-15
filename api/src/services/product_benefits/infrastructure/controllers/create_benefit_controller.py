from src.core.database import AsyncSessionLocal
from src.services.product_benefits.application.usecase.create_benefit_use_case import (
    CreateBenefitUseCase,
)
from src.services.product_benefits.domain.dto.benefit_schema import (
    BenefitResponse,
    CreateBenefitRequest,
)
from src.services.product_benefits.infrastructure.adapters.postgres import PostgresBenefitRepository
from src.services.products.infrastructure.adapters.postgres import PostgresProductRepository


async def create(product_id: int, body: CreateBenefitRequest) -> BenefitResponse:
    benefit_repo = PostgresBenefitRepository(AsyncSessionLocal)
    product_repo = PostgresProductRepository(AsyncSessionLocal)
    use_case = CreateBenefitUseCase(benefit_repo, product_repo)
    benefit = await use_case.execute(product_id, body.title, body.description)
    return BenefitResponse.from_entity(benefit)