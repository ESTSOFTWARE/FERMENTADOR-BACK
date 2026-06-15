from src.core.database import AsyncSessionLocal
from src.services.product_reviews.application.usecase.create_review_use_case import (
    CreateReviewUseCase,
)
from src.services.product_reviews.domain.dto.review_schema import (
    CreateReviewRequest,
    ReviewResponse,
)
from src.services.product_reviews.infrastructure.adapters.postgres import PostgresReviewRepository
from src.services.products.infrastructure.adapters.postgres import PostgresProductRepository


async def create(product_id: int, body: CreateReviewRequest, current_user: dict) -> ReviewResponse:
    review_repo  = PostgresReviewRepository(AsyncSessionLocal)
    product_repo = PostgresProductRepository(AsyncSessionLocal)
    use_case = CreateReviewUseCase(review_repo, product_repo)
    review = await use_case.execute(
        product_id=product_id,
        user_id=current_user["id"],
        rating=body.rating,
        comment=body.comment
    )
    return ReviewResponse.from_entity(review)