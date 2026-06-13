from src.core.exceptions import ForbiddenException, ReviewNotFoundException
from src.services.product_reviews.domain.repository import IReviewRepository
from src.services.products.domain.repository import IProductRepository


class DeleteReviewUseCase:
    def __init__(self, review_repository: IReviewRepository, product_repository: IProductRepository):
        self._review_repo  = review_repository
        self._product_repo = product_repository

    async def execute(self, product_id: int, review_id: int, user_id: int, is_admin: bool) -> None:
        review = await self._review_repo.get_by_id(review_id)
        if not review:
            raise ReviewNotFoundException()

        if review.product_id != product_id:
            raise ReviewNotFoundException()

        # Solo el autor o un admin pueden eliminar
        if not is_admin and review.user_id != user_id:
            raise ForbiddenException()

        await self._review_repo.delete(review_id)

        # Recalcular rating del producto
        new_rating = await self._review_repo.average_rating_by_product(product_id)
        await self._product_repo.update_rating(product_id, new_rating)