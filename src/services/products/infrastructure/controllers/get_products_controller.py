from src.core.database import AsyncSessionLocal
from src.services.products.application.usecase.get_products_use_case import GetProductsUseCase
from src.services.products.domain.dto.product_schema import ProductResponse
from src.services.products.infrastructure.adapters.MySQL import MySQLProductRepository


async def get_all(page: int = 1, limit: int = 10, search: str | None = None) -> dict:
    repo = MySQLProductRepository(AsyncSessionLocal)
    use_case = GetProductsUseCase(repo)
    products, total = await use_case.execute(page, limit, search)
    return {
        "items": [ProductResponse.from_entity(p) for p in products],
        "total": total,
        "page": page,
        "limit": limit
    }
