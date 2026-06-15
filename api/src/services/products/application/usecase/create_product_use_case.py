from src.core.exceptions import ProductAlreadyExistsException
from src.services.products.domain.entities.product import Product
from src.services.products.domain.repository import IProductRepository


class CreateProductUseCase:
    def __init__(self, product_repository: IProductRepository):
        self._product_repo = product_repository

    async def execute(
        self, name: str, description: str, price: float,
        sku: str, stock: int, category_id: int | None
    ) -> Product:
        existing = await self._product_repo.get_by_sku(sku)
        if existing:
            raise ProductAlreadyExistsException()

        return await self._product_repo.create(Product(
            id=None,
            name=name,
            description=description,
            price=price,
            sku=sku,
            stock=stock,
            rating=0,
            category_id=category_id
        ))