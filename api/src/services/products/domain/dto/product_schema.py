from datetime import datetime

from pydantic import BaseModel, Field


class CreateProductRequest(BaseModel):
    name:        str        = Field(..., min_length=1, max_length=150)
    description: str        = Field(..., min_length=1)
    price:       float      = Field(..., gt=0)
    sku:         str        = Field(..., min_length=1, max_length=50)
    stock:       int        = Field(0, ge=0)
    category_id: int | None = None


class UpdateProductRequest(BaseModel):
    name:        str | None   = Field(None, min_length=1, max_length=150)
    description: str | None   = Field(None, min_length=1)
    price:       float | None = Field(None, gt=0)
    sku:         str | None   = Field(None, min_length=1, max_length=50)
    stock:       int | None   = Field(None, ge=0)
    category_id: int | None   = None


class ProductResponse(BaseModel):
    id:          int
    name:        str
    description: str
    price:       float
    sku:         str
    stock:       int
    rating:      float
    category_id: int | None
    created_at:  datetime
    updated_at:  datetime

    @classmethod
    def from_entity(cls, product) -> "ProductResponse":
        return cls(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            sku=product.sku,
            stock=product.stock,
            rating=product.rating,
            category_id=product.category_id,
            created_at=product.created_at,
            updated_at=product.updated_at
        )