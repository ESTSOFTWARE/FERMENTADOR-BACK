from src.core.exceptions import ProductNotFoundException, ProductAlreadyExistsException
from src.services.products.domain.entities.product import Product
from src.services.products.domain.repository import IProductRepository

class UpdateProductUseCase:
    def __init__(self, product_repository: IProductRepository):
        self._product_repo = product_repository

    async def execute(self, product_id: int, **kwargs) -> Product:
        product = await self._product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException()

        if "sku" in kwargs and kwargs["sku"] != product.sku:
            existing = await self._product_repo.get_by_sku(kwargs["sku"])
            if existing:
                raise ProductAlreadyExistsException()

        for key, value in kwargs.items():
            if value is not None:
                setattr(product, key, value)

        return await self._product_repo.update(product)
