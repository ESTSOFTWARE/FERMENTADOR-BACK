from src.core.database import AsyncSessionLocal
from src.services.product_specifications.application.usecase.get_specifications_use_case import (
    GetSpecificationsUseCase,
)
from src.services.product_specifications.domain.dto.specification_schema import (
    SpecificationResponse,
)
from src.services.product_specifications.infrastructure.adapters.postgres import (
    PostgresSpecificationRepository,
)
from src.services.products.infrastructure.adapters.postgres import PostgresProductRepository


async def get_all(product_id: int) -> list[SpecificationResponse]:
    spec_repo    = PostgresSpecificationRepository(AsyncSessionLocal)
    product_repo = PostgresProductRepository(AsyncSessionLocal)
    use_case = GetSpecificationsUseCase(spec_repo, product_repo)
    specs = await use_case.execute(product_id)
    return [SpecificationResponse.from_entity(s) for s in specs]