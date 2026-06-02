from src.core.database import AsyncSessionLocal
from src.services.products.application.usecase.get_product_by_id_use_case import (
    GetProductByIdUseCase,
)
from src.services.products.domain.dto.product_schema import ProductResponse
from src.services.products.infrastructure.adapters.MySQL import MySQLProductRepository


async def get_by_id(product_id: int) -> ProductResponse:
    repo = MySQLProductRepository(AsyncSessionLocal)
    use_case = GetProductByIdUseCase(repo)
    product = await use_case.execute(product_id)
    return ProductResponse.from_entity(product)
