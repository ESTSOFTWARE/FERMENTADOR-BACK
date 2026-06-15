from datetime import datetime

from pydantic import BaseModel, Field


class CreateCategoryRequest(BaseModel):
    name:        str        = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1)


class UpdateCategoryRequest(BaseModel):
    name:        str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1)


class CategoryResponse(BaseModel):
    id:          int
    name:        str
    description: str | None
    created_at:  datetime
    updated_at:  datetime

    @classmethod
    def from_entity(cls, category) -> "CategoryResponse":
        return cls(
            id=category.id,
            name=category.name,
            description=category.description,
            created_at=category.created_at,
            updated_at=category.updated_at
        )