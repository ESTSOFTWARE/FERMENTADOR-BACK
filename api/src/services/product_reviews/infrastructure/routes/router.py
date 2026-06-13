from fastapi import APIRouter, Depends, Query

from src.core.dependencies import get_current_user
from src.services.product_reviews.domain.dto.review_schema import (
    CreateReviewRequest,
    ReviewListResponse,
    ReviewResponse,
)
from src.services.product_reviews.infrastructure.controllers.create_review_controller import create
from src.services.product_reviews.infrastructure.controllers.delete_review_controller import delete
from src.services.product_reviews.infrastructure.controllers.get_reviews_controller import get_all

router = APIRouter()


@router.get("/", response_model=ReviewListResponse, summary="Obtener reseñas del producto")
async def get_reviews(
    product_id: int,
    page:  int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    return await get_all(product_id, page, limit)


@router.post("/", response_model=ReviewResponse, status_code=201, summary="Crear reseña (usuario autenticado)")
async def create_review(
    product_id: int,
    body: CreateReviewRequest,
    current_user: dict = Depends(get_current_user)
):
    return await create(product_id, body, current_user)


@router.delete("/{review_id}", status_code=200, summary="Eliminar reseña (autor o admin)")
async def delete_review(
    product_id: int,
    review_id: int,
    current_user: dict = Depends(get_current_user)
):
    return await delete(product_id, review_id, current_user)