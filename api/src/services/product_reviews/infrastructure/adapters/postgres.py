from sqlalchemy import delete, func, select

from src.core.models.product_review_model import ProductReviewModel
from src.services.product_reviews.domain.entities.review import Review
from src.services.product_reviews.domain.repository import IReviewRepository


class PostgresReviewRepository(IReviewRepository):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def get_by_product(self, product_id: int, page: int, limit: int) -> list[Review]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProductReviewModel)
                .where(ProductReviewModel.product_id == product_id)
                .order_by(ProductReviewModel.created_at.desc())
                .offset((page - 1) * limit)
                .limit(limit)
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, review_id: int) -> Review | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProductReviewModel).where(ProductReviewModel.id == review_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def get_by_user_and_product(self, user_id: int, product_id: int) -> Review | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProductReviewModel).where(
                    ProductReviewModel.user_id == user_id,
                    ProductReviewModel.product_id == product_id
                )
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def count_by_product(self, product_id: int) -> int:
        async with self._session_factory() as session:
            result = await session.execute(
                select(func.count()).select_from(ProductReviewModel)
                .where(ProductReviewModel.product_id == product_id)
            )
            return result.scalar()

    async def average_rating_by_product(self, product_id: int) -> float:
        async with self._session_factory() as session:
            result = await session.execute(
                select(func.avg(ProductReviewModel.rating))
                .where(ProductReviewModel.product_id == product_id)
            )
            avg = result.scalar()
            return round(float(avg), 2) if avg is not None else 0.0

    async def create(self, review: Review) -> Review:
        async with self._session_factory() as session:
            model = ProductReviewModel(
                product_id=review.product_id,
                user_id=review.user_id,
                rating=review.rating,
                comment=review.comment
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def delete(self, review_id: int) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(ProductReviewModel).where(ProductReviewModel.id == review_id)
            )
            await session.commit()

    def _to_entity(self, model: ProductReviewModel) -> Review:
        return Review(
            id=model.id,
            product_id=model.product_id,
            user_id=model.user_id,
            rating=model.rating,
            comment=model.comment,
            created_at=model.created_at
        )