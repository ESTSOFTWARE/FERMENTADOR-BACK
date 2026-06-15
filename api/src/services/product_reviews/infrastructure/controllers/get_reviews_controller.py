from src.core.database import AsyncSessionLocal
from src.services.product_reviews.application.usecase.get_reviews_use_case import GetReviewsUseCase
from src.services.product_reviews.domain.dto.review_schema import ReviewListResponse, ReviewResponse
from src.services.product_reviews.infrastructure.adapters.postgres import PostgresReviewRepository
from src.services.products.infrastructure.adapters.postgres import PostgresProductRepository


async def get_all(product_id: int, page: int, limit: int) -> ReviewListResponse:
    review_repo  = PostgresReviewRepository(AsyncSessionLocal)
    product_repo = PostgresProductRepository(AsyncSessionLocal)
    use_case = GetReviewsUseCase(review_repo, product_repo)
    data = await use_case.execute(product_id, page, limit)
    return ReviewListResponse(
        items=[ReviewResponse.from_entity(r) for r in data["items"]],
        total=data["total"],
        page=data["page"],
        limit=data["limit"],
        average_rating=data["average_rating"]
    )