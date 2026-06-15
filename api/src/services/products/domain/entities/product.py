from dataclasses import dataclass
from datetime import datetime


@dataclass
class Product:
    id:          int | None
    name:        str
    description: str
    price:       float
    sku:         str
    stock:       int
    rating:      float
    category_id: int | None = None
    created_at:  datetime | None = None
    updated_at:  datetime | None = None