from sqlalchemy import delete, select, update

from src.core.models.product_benefit_model import ProductBenefitModel
from src.services.product_benefits.domain.entities.benefit import Benefit
from src.services.product_benefits.domain.repository import IBenefitRepository


class PostgresBenefitRepository(IBenefitRepository):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def get_by_product(self, product_id: int) -> list[Benefit]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProductBenefitModel)
                .where(ProductBenefitModel.product_id == product_id)
                .order_by(ProductBenefitModel.id.asc())
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, benefit_id: int) -> Benefit | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProductBenefitModel).where(ProductBenefitModel.id == benefit_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def create(self, benefit: Benefit) -> Benefit:
        async with self._session_factory() as session:
            model = ProductBenefitModel(
                product_id=benefit.product_id,
                title=benefit.title,
                description=benefit.description
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def update(self, benefit: Benefit) -> Benefit:
        async with self._session_factory() as session:
            await session.execute(
                update(ProductBenefitModel)
                .where(ProductBenefitModel.id == benefit.id)
                .values(
                    title=benefit.title,
                    description=benefit.description
                )
            )
            await session.commit()
            result = await session.execute(
                select(ProductBenefitModel).where(ProductBenefitModel.id == benefit.id)
            )
            return self._to_entity(result.scalar_one())

    async def delete(self, benefit_id: int) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(ProductBenefitModel).where(ProductBenefitModel.id == benefit_id)
            )
            await session.commit()

    def _to_entity(self, model: ProductBenefitModel) -> Benefit:
        return Benefit(
            id=model.id,
            product_id=model.product_id,
            title=model.title,
            description=model.description,
            created_at=model.created_at
        )