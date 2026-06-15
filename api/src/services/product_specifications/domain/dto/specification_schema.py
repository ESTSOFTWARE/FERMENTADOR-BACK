from datetime import datetime

from pydantic import BaseModel, Field


class CreateSpecificationRequest(BaseModel):
    name:  str = Field(..., min_length=1, max_length=150)
    value: str = Field(..., min_length=1)


class UpdateSpecificationRequest(BaseModel):
    name:  str | None = Field(None, min_length=1, max_length=150)
    value: str | None = Field(None, min_length=1)


class SpecificationResponse(BaseModel):
    id:         int
    product_id: int
    name:       str
    value:      str
    created_at: datetime

    @classmethod
    def from_entity(cls, spec) -> "SpecificationResponse":
        return cls(
            id=spec.id,
            product_id=spec.product_id,
            name=spec.name,
            value=spec.value,
            created_at=spec.created_at
        )