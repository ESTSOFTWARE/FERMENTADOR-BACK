from src.core.exceptions import ProductNotFoundException
from src.services.product_reviews.domain.repository import IReviewRepository
from src.services.products.domain.repository import IProductRepository


class GetReviewsUseCase:
    def __init__(self, review_repository: IReviewRepository, product_repository: IProductRepository):
        self._review_repo  = review_repository
        self._product_repo = product_repository

    async def execute(self, product_id: int, page: int, limit: int) -> dict:
        product = await self._product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException()

        reviews        = await self._review_repo.get_by_product(product_id, page, limit)
        total          = await self._review_repo.count_by_product(product_id)
        average_rating = await self._review_repo.average_rating_by_product(product_id)

        return {
            "items":          reviews,
            "total":          total,
            "page":           page,
            "limit":          limit,
            "average_rating": average_rating
        }