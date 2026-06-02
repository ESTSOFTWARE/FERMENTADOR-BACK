from sqlalchemy import select, update, delete, func, or_
from src.core.models.product_model import ProductModel
from src.services.products.domain.entities.product import Product
from src.services.products.domain.repository import IProductRepository

class MySQLProductRepository(IProductRepository):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def get_all(self, page: int = 1, limit: int = 10, search: str | None = None) -> list[Product]:
        async with self._session_factory() as session:
            query = select(ProductModel)
            if search:
                query = query.where(
                    or_(
                        ProductModel.name.ilike(f"%{search}%"),
                        ProductModel.sku.ilike(f"%{search}%"),
                        ProductModel.description.ilike(f"%{search}%")
                    )
                )
            query = query.offset((page - 1) * limit).limit(limit).order_by(ProductModel.id.desc())
            result = await session.execute(query)
            return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, product_id: int) -> Product | None:
        async with self._session_factory() as session:
            query = select(ProductModel).where(ProductModel.id == product_id)
            result = await session.execute(query)
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def get_by_sku(self, sku: str) -> Product | None:
        async with self._session_factory() as session:
            query = select(ProductModel).where(ProductModel.sku == sku)
            result = await session.execute(query)
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def create(self, product: Product) -> Product:
        async with self._session_factory() as session:
            model = ProductModel(
                name=product.name,
                description=product.description,
                price=product.price,
                sku=product.sku,
                stock=product.stock,
                rating=product.rating
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def update(self, product: Product) -> Product:
        async with self._session_factory() as session:
            await session.execute(
                update(ProductModel)
                .where(ProductModel.id == product.id)
                .values(
                    name=product.name,
                    description=product.description,
                    price=product.price,
                    sku=product.sku,
                    stock=product.stock,
                    rating=product.rating
                )
            )
            await session.commit()
            return product

    async def delete(self, product_id: int) -> None:
        async with self._session_factory() as session:
            await session.execute(delete(ProductModel).where(ProductModel.id == product_id))
            await session.commit()

    async def count(self, search: str | None = None) -> int:
        async with self._session_factory() as session:
            query = select(func.count()).select_from(ProductModel)
            if search:
                query = query.where(
                    or_(
                        ProductModel.name.ilike(f"%{search}%"),
                        ProductModel.sku.ilike(f"%{search}%"),
                        ProductModel.description.ilike(f"%{search}%")
                    )
                )
            result = await session.execute(query)
            return result.scalar()

    def _to_entity(self, model: ProductModel) -> Product:
        return Product(
            id=model.id,
            name=model.name,
            description=model.description,
            price=model.price,
            sku=model.sku,
            stock=model.stock,
            rating=model.rating,
            created_at=model.created_at
        )
