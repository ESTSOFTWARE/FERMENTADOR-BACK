from dataclasses import dataclass
from datetime import datetime


@dataclass
class Include:
    id:          int | None
    product_id:  int
    description: str
    created_at:  datetime | None = None