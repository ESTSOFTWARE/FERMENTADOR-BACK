from src.core.database import AsyncSessionLocal
from src.services.product_benefits.application.usecase.update_benefit_use_case import (
    UpdateBenefitUseCase,
)
from src.services.product_benefits.domain.dto.benefit_schema import (
    BenefitResponse,
    UpdateBenefitRequest,
)
from src.services.product_benefits.infrastructure.adapters.postgres import PostgresBenefitRepository


async def update(product_id: int, benefit_id: int, body: UpdateBenefitRequest) -> BenefitResponse:
    repo = PostgresBenefitRepository(AsyncSessionLocal)
    use_case = UpdateBenefitUseCase(repo)
    benefit = await use_case.execute(product_id, benefit_id, **body.model_dump(exclude_unset=True))
    return BenefitResponse.from_entity(benefit)