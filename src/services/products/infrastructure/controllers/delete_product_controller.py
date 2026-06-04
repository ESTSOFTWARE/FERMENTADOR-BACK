from src.core.database import AsyncSessionLocal
from src.services.products.application.usecase.delete_product_use_case import DeleteProductUseCase
from src.services.products.infrastructure.adapters.postgres import PostgresProductRepository


async def delete(product_id: int) -> dict:
    repo = PostgresProductRepository(AsyncSessionLocal)
    use_case = DeleteProductUseCase(repo)
    await use_case.execute(product_id)
    return {"message": "Producto eliminado exitosamente"}
