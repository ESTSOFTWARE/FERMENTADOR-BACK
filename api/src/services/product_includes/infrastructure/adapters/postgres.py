from sqlalchemy import delete, select, update

from src.core.models.product_include_model import ProductIncludeModel
from src.services.product_includes.domain.entities.include import Include
from src.services.product_includes.domain.repository import IIncludeRepository


class PostgresIncludeRepository(IIncludeRepository):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def get_by_product(self, product_id: int) -> list[Include]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProductIncludeModel)
                .where(ProductIncludeModel.product_id == product_id)
                .order_by(ProductIncludeModel.id.asc())
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, include_id: int) -> Include | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProductIncludeModel).where(ProductIncludeModel.id == include_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def create(self, include: Include) -> Include:
        async with self._session_factory() as session:
            model = ProductIncludeModel(
                product_id=include.product_id,
                description=include.description
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def update(self, include: Include) -> Include:
        async with self._session_factory() as session:
            await session.execute(
                update(ProductIncludeModel)
                .where(ProductIncludeModel.id == include.id)
                .values(description=include.description)
            )
            await session.commit()
            result = await session.execute(
                select(ProductIncludeModel).where(ProductIncludeModel.id == include.id)
            )
            return self._to_entity(result.scalar_one())

    async def delete(self, include_id: int) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(ProductIncludeModel).where(ProductIncludeModel.id == include_id)
            )
            await session.commit()

    def _to_entity(self, model: ProductIncludeModel) -> Include:
        return Include(
            id=model.id,
            product_id=model.product_id,
            description=model.description,
            created_at=model.created_at
        )