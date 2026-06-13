from dataclasses import dataclass
from datetime import datetime


@dataclass
class Review:
    id:         int | None
    product_id: int
    user_id:    int
    rating:     int
    comment:    str | None
    created_at: datetime | None = None