from src.core.database import AsyncSessionLocal
from src.services.product_specifications.application.usecase.update_specification_use_case import (
    UpdateSpecificationUseCase,
)
from src.services.product_specifications.domain.dto.specification_schema import (
    SpecificationResponse,
    UpdateSpecificationRequest,
)
from src.services.product_specifications.infrastructure.adapters.postgres import (
    PostgresSpecificationRepository,
)


async def update(product_id: int, specification_id: int, body: UpdateSpecificationRequest) -> SpecificationResponse:
    repo = PostgresSpecificationRepository(AsyncSessionLocal)
    use_case = UpdateSpecificationUseCase(repo)
    spec = await use_case.execute(product_id, specification_id, **body.model_dump(exclude_unset=True))
    return SpecificationResponse.from_entity(spec)