from datetime import datetime

from pydantic import BaseModel, Field


class CreateIncludeRequest(BaseModel):
    description: str = Field(..., min_length=1)


class UpdateIncludeRequest(BaseModel):
    description: str | None = Field(None, min_length=1)


class IncludeResponse(BaseModel):
    id:          int
    product_id:  int
    description: str
    created_at:  datetime

    @classmethod
    def from_entity(cls, include) -> "IncludeResponse":
        return cls(
            id=include.id,
            product_id=include.product_id,
            description=include.description,
            created_at=include.created_at
        )