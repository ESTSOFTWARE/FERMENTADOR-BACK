from src.core.database import AsyncSessionLocal
from src.services.product_includes.application.usecase.get_includes_use_case import (
    GetIncludesUseCase,
)
from src.services.product_includes.domain.dto.include_schema import IncludeResponse
from src.services.product_includes.infrastructure.adapters.postgres import PostgresIncludeRepository
from src.services.products.infrastructure.adapters.postgres import PostgresProductRepository


async def get_all(product_id: int) -> list[IncludeResponse]:
    include_repo = PostgresIncludeRepository(AsyncSessionLocal)
    product_repo = PostgresProductRepository(AsyncSessionLocal)
    use_case = GetIncludesUseCase(include_repo, product_repo)
    includes = await use_case.execute(product_id)
    return [IncludeResponse.from_entity(i) for i in includes]