from src.core.database import AsyncSessionLocal
from src.services.product_includes.application.usecase.update_include_use_case import (
    UpdateIncludeUseCase,
)
from src.services.product_includes.domain.dto.include_schema import (
    IncludeResponse,
    UpdateIncludeRequest,
)
from src.services.product_includes.infrastructure.adapters.postgres import PostgresIncludeRepository


async def update(product_id: int, include_id: int, body: UpdateIncludeRequest) -> IncludeResponse:
    repo = PostgresIncludeRepository(AsyncSessionLocal)
    use_case = UpdateIncludeUseCase(repo)
    include = await use_case.execute(product_id, include_id, **body.model_dump(exclude_unset=True))
    return IncludeResponse.from_entity(include)