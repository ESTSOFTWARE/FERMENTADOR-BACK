from dataclasses import dataclass
from datetime import datetime


@dataclass
class Benefit:
    id:          int | None
    product_id:  int
    title:       str
    description: str | None
    created_at:  datetime | None = None