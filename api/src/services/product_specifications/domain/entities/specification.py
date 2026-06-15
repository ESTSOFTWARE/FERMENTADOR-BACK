from dataclasses import dataclass
from datetime import datetime


@dataclass
class Specification:
    id:         int | None
    product_id: int
    name:       str
    value:      str
    created_at: datetime | None = None