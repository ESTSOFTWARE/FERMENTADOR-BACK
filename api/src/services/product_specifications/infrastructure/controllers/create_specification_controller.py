from src.core.database import AsyncSessionLocal
from src.services.product_specifications.application.usecase.create_specification_use_case import (
    CreateSpecificationUseCase,
)
from src.services.product_specifications.domain.dto.specification_schema import (
    CreateSpecificationRequest,
    SpecificationResponse,
)
from src.services.product_specifications.infrastructure.adapters.postgres import (
    PostgresSpecificationRepository,
)
from src.services.products.infrastructure.adapters.postgres import PostgresProductRepository


async def create(product_id: int, body: CreateSpecificationRequest) -> SpecificationResponse:
    spec_repo    = PostgresSpecificationRepository(AsyncSessionLocal)
    product_repo = PostgresProductRepository(AsyncSessionLocal)
    use_case = CreateSpecificationUseCase(spec_repo, product_repo)
    spec = await use_case.execute(product_id, body.name, body.value)
    return SpecificationResponse.from_entity(spec)