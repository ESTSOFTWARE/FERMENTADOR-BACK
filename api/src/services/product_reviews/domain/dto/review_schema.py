from datetime import datetime

from pydantic import BaseModel, Field


class CreateReviewRequest(BaseModel):
    rating:  int        = Field(..., ge=1, le=5)
    comment: str | None = Field(None, max_length=1000)


class ReviewResponse(BaseModel):
    id:         int
    product_id: int
    user_id:    int
    rating:     int
    comment:    str | None
    created_at: datetime

    @classmethod
    def from_entity(cls, review) -> "ReviewResponse":
        return cls(
            id=review.id,
            product_id=review.product_id,
            user_id=review.user_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at
        )


class ReviewListResponse(BaseModel):
    items:        list[ReviewResponse]
    total:        int
    page:         int
    limit:        int
    average_rating: float