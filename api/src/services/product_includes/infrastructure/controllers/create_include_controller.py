from src.core.database import AsyncSessionLocal
from src.services.product_includes.application.usecase.create_include_use_case import (
    CreateIncludeUseCase,
)
from src.services.product_includes.domain.dto.include_schema import (
    CreateIncludeRequest,
    IncludeResponse,
)
from src.services.product_includes.infrastructure.adapters.postgres import PostgresIncludeRepository
from src.services.products.infrastructure.adapters.postgres import PostgresProductRepository


async def create(product_id: int, body: CreateIncludeRequest) -> IncludeResponse:
    include_repo = PostgresIncludeRepository(AsyncSessionLocal)
    product_repo = PostgresProductRepository(AsyncSessionLocal)
    use_case = CreateIncludeUseCase(include_repo, product_repo)
    include = await use_case.execute(product_id, body.description)
    return IncludeResponse.from_entity(include)