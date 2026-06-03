from src.core.database import AsyncSessionLocal
from src.services.products.application.usecase.create_product_use_case import CreateProductUseCase
from src.services.products.domain.dto.product_schema import CreateProductRequest, ProductResponse
from src.services.products.infrastructure.adapters.MySQL import MySQLProductRepository


async def create(body: CreateProductRequest) -> ProductResponse:
    repo = MySQLProductRepository(AsyncSessionLocal)
    use_case = CreateProductUseCase(repo)
    product = await use_case.execute(
        name=body.name,
        description=body.description,
        price=body.price,
        sku=body.sku,
        stock=body.stock,
        rating=body.rating
    )
    return ProductResponse.from_entity(product)
