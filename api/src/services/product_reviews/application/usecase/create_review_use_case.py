from src.core.exceptions import ProductNotFoundException, ReviewAlreadyExistsException
from src.services.product_reviews.domain.entities.review import Review
from src.services.product_reviews.domain.repository import IReviewRepository
from src.services.products.domain.repository import IProductRepository


class CreateReviewUseCase:
    def __init__(self, review_repository: IReviewRepository, product_repository: IProductRepository):
        self._review_repo  = review_repository
        self._product_repo = product_repository

    async def execute(self, product_id: int, user_id: int, rating: int, comment: str | None) -> Review:
        product = await self._product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException()

        existing = await self._review_repo.get_by_user_and_product(user_id, product_id)
        if existing:
            raise ReviewAlreadyExistsException()

        review = await self._review_repo.create(Review(
            id=None,
            product_id=product_id,
            user_id=user_id,
            rating=rating,
            comment=comment
        ))

        # Recalcular rating del producto
        new_rating = await self._review_repo.average_rating_by_product(product_id)
        await self._product_repo.update_rating(product_id, new_rating)

        return review