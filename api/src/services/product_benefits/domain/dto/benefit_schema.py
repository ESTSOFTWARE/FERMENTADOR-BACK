from datetime import datetime

from pydantic import BaseModel, Field


class CreateBenefitRequest(BaseModel):
    title:       str        = Field(..., min_length=1, max_length=150)
    description: str | None = Field(None, min_length=1)


class UpdateBenefitRequest(BaseModel):
    title:       str | None = Field(None, min_length=1, max_length=150)
    description: str | None = Field(None, min_length=1)


class BenefitResponse(BaseModel):
    id:          int
    product_id:  int
    title:       str
    description: str | None
    created_at:  datetime

    @classmethod
    def from_entity(cls, benefit) -> "BenefitResponse":
        return cls(
            id=benefit.id,
            product_id=benefit.product_id,
            title=benefit.title,
            description=benefit.description,
            created_at=benefit.created_at
        )