from src.core.database import AsyncSessionLocal
from src.services.products.application.usecase.update_product_use_case import UpdateProductUseCase
from src.services.products.domain.dto.product_schema import UpdateProductRequest, ProductResponse
from src.services.products.infrastructure.adapters.MySQL import MySQLProductRepository

async def update(product_id: int, body: UpdateProductRequest) -> ProductResponse:
    repo = MySQLProductRepository(AsyncSessionLocal)
    use_case = UpdateProductUseCase(repo)
    product = await use_case.execute(product_id, **body.model_dump(exclude_unset=True))
    return ProductResponse.from_entity(product)
