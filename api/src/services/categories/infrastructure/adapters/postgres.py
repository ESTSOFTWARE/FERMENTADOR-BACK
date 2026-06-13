from sqlalchemy import delete, select, update

from src.core.models.category_model import ProductCategoryModel
from src.services.categories.domain.entities.category import Category
from src.services.categories.domain.repository import ICategoryRepository


class PostgresCategoryRepository(ICategoryRepository):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def get_all(self) -> list[Category]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProductCategoryModel).order_by(ProductCategoryModel.name)
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, category_id: int) -> Category | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProductCategoryModel).where(ProductCategoryModel.id == category_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def get_by_name(self, name: str) -> Category | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProductCategoryModel).where(ProductCategoryModel.name == name)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def create(self, category: Category) -> Category:
        async with self._session_factory() as session:
            model = ProductCategoryModel(
                name=category.name,
                description=category.description
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def update(self, category: Category) -> Category:
        async with self._session_factory() as session:
            await session.execute(
                update(ProductCategoryModel)
                .where(ProductCategoryModel.id == category.id)
                .values(
                    name=category.name,
                    description=category.description
                )
            )
            await session.commit()
            result = await session.execute(
                select(ProductCategoryModel).where(ProductCategoryModel.id == category.id)
            )
            model = result.scalar_one()
            return self._to_entity(model)

    async def delete(self, category_id: int) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(ProductCategoryModel).where(ProductCategoryModel.id == category_id)
            )
            await session.commit()

    def _to_entity(self, model: ProductCategoryModel) -> Category:
        return Category(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at
        )