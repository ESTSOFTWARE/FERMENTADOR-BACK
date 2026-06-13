from sqlalchemy import delete, select, update

from src.core.models.product_specification_model import ProductSpecificationModel
from src.services.product_specifications.domain.entities.specification import Specification
from src.services.product_specifications.domain.repository import ISpecificationRepository


class PostgresSpecificationRepository(ISpecificationRepository):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def get_by_product(self, product_id: int) -> list[Specification]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProductSpecificationModel)
                .where(ProductSpecificationModel.product_id == product_id)
                .order_by(ProductSpecificationModel.id.asc())
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, specification_id: int) -> Specification | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProductSpecificationModel).where(ProductSpecificationModel.id == specification_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def create(self, specification: Specification) -> Specification:
        async with self._session_factory() as session:
            model = ProductSpecificationModel(
                product_id=specification.product_id,
                name=specification.name,
                value=specification.value
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def update(self, specification: Specification) -> Specification:
        async with self._session_factory() as session:
            await session.execute(
                update(ProductSpecificationModel)
                .where(ProductSpecificationModel.id == specification.id)
                .values(
                    name=specification.name,
                    value=specification.value
                )
            )
            await session.commit()
            result = await session.execute(
                select(ProductSpecificationModel).where(ProductSpecificationModel.id == specification.id)
            )
            return self._to_entity(result.scalar_one())

    async def delete(self, specification_id: int) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(ProductSpecificationModel).where(ProductSpecificationModel.id == specification_id)
            )
            await session.commit()

    def _to_entity(self, model: ProductSpecificationModel) -> Specification:
        return Specification(
            id=model.id,
            product_id=model.product_id,
            name=model.name,
            value=model.value,
            created_at=model.created_at
        )