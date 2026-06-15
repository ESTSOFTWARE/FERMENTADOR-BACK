from src.core.database import AsyncSessionLocal
from src.services.product_reviews.application.usecase.delete_review_use_case import (
    DeleteReviewUseCase,
)
from src.services.product_reviews.infrastructure.adapters.postgres import PostgresReviewRepository
from src.services.products.infrastructure.adapters.postgres import PostgresProductRepository


async def delete(product_id: int, review_id: int, current_user: dict) -> dict:
    review_repo  = PostgresReviewRepository(AsyncSessionLocal)
    product_repo = PostgresProductRepository(AsyncSessionLocal)
    use_case = DeleteReviewUseCase(review_repo, product_repo)
    await use_case.execute(
        product_id=product_id,
        review_id=review_id,
        user_id=current_user["id"],
        is_admin=current_user.get("role") == "admin"
    )
    return {"message": "Reseña eliminada exitosamente"}