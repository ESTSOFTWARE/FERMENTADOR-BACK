from src.core.database import AsyncSessionLocal
from src.services.products.application.usecase.get_related_products_use_case import (
    GetRelatedProductsUseCase,
)
from src.services.products.domain.dto.product_schema import ProductResponse
from src.services.products.infrastructure.adapters.postgres import PostgresProductRepository


async def get_related(product_id: int, limit: int = 6) -> list[ProductResponse]:
    repo = PostgresProductRepository(AsyncSessionLocal)
    use_case = GetRelatedProductsUseCase(repo)
    products = await use_case.execute(product_id, limit)
    return [ProductResponse.from_entity(p) for p in products]