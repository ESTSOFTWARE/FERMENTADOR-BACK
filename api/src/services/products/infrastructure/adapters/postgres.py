from sqlalchemy import delete, func, or_, select, update

from src.core.models.product_model import ProductModel
from src.services.products.domain.entities.product import Product
from src.services.products.domain.repository import IProductRepository


class PostgresProductRepository(IProductRepository):
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
            result = await session.execute(
                select(ProductModel).where(ProductModel.id == product_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def get_by_sku(self, sku: str) -> Product | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProductModel).where(ProductModel.sku == sku)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def get_related(self, product_id: int, category_id: int, limit: int = 6) -> list[Product]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProductModel)
                .where(
                    ProductModel.category_id == category_id,
                    ProductModel.id != product_id
                )
                .limit(limit)
                .order_by(ProductModel.id.desc())
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def update_rating(self, product_id: int, rating: float) -> None:
        async with self._session_factory() as session:
            await session.execute(
                update(ProductModel)
                .where(ProductModel.id == product_id)
                .values(rating=rating)
            )
            await session.commit()

    async def create(self, product: Product) -> Product:
        async with self._session_factory() as session:
            model = ProductModel(
                name=product.name,
                description=product.description,
                price=product.price,
                sku=product.sku,
                stock=product.stock,
                rating=0,
                image=product.image,
                category_id=product.category_id
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
                    image=product.image,
                    category_id=product.category_id
                )
            )
            await session.commit()
            result = await session.execute(
                select(ProductModel).where(ProductModel.id == product.id)
            )
            model = result.scalar_one()
            return self._to_entity(model)

    async def delete(self, product_id: int) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(ProductModel).where(ProductModel.id == product_id)
            )
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
            rating=float(model.rating),
            image=model.image,
            category_id=model.category_id,
            created_at=model.created_at,
            updated_at=model.updated_at
        )